"""
Session Chain Management

Replaces step_session with Celery chains for automatic job sequencing.
Celery tasks automatically chain to the next job when they complete.
"""
import fcntl
import logging
import time
import traceback
from pathlib import Path
from typing import Optional, List, Tuple
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo

from celery import chain
from celery_app import app

from lib.session_manager import load_session, save_session, SessionStatus
from lib.job_manager import save_job, load_job, JobStatus, get_redis_client
from config import config

logger = logging.getLogger(__name__)


def dispatch_next_job_in_chain(session_id: str, completed_job_type: str = None) -> Optional[str]:
    """
    Dispatch the next job in a session's job_plan that doesn't have a job_id yet.
    This is called automatically by Celery tasks when they complete.
    
    Uses file locking (flock) on the session file to prevent race conditions.
    
    Args:
        session_id: Session ID
        completed_job_type: Type of job that just completed (for logging)
        
    Returns:
        Task ID of dispatched job, or None if no more jobs
    """
    dispatch_start = time.time()
    logger.info(f"\n{'='*80}")
    logger.info(f"🔵 [DISPATCH] DISPATCH_NEXT_JOB_IN_CHAIN called for session {session_id}")
    logger.info(f"   Timestamp: {datetime.now().isoformat()}")
    if completed_job_type:
        logger.info(f"   Triggered by completed job: {completed_job_type}")
    else:
        logger.info(f"   Initial dispatch (no previous job completed)")
    logger.info(f"{'='*80}")
    
    # Use Redis for atomic dispatch coordination (simpler than file locks, no permission issues)
    # Only ONE process should dispatch jobs for a session at a time
    redis_client = get_redis_client()
    dispatch_lock_key = f"dispatch_lock:{session_id}"
    lock_ttl = 30  # 30 second lock timeout (dispatch should be fast)
    lock_acquired = False
    lock_acquire_start = time.time()
    max_lock_wait = 10.0  # 10 seconds max wait
    poll_interval = 0.1  # Poll every 100ms
    
    try:
        logger.debug(f"🔒 Acquiring Redis dispatch lock for session {session_id}")
        
        # Try to acquire lock with SETNX (set if not exists) - atomic operation
        # Value is timestamp so we can detect stale locks
        lock_value = str(time.time())
        lock_acquired = redis_client.set(dispatch_lock_key, lock_value, nx=True, ex=lock_ttl)
        
        if not lock_acquired:
            # Lock is held - poll with timeout
            logger.debug(f"   Lock is held by another process, waiting up to {max_lock_wait:.1f} seconds...")
            elapsed = 0.0
            while elapsed < max_lock_wait:
                time.sleep(poll_interval)
                elapsed = time.time() - lock_acquire_start
                lock_acquired = redis_client.set(dispatch_lock_key, str(time.time()), nx=True, ex=lock_ttl)
                if lock_acquired:
                    break
            
            if not lock_acquired:
                lock_elapsed = time.time() - lock_acquire_start
                error_msg = f"Failed to acquire dispatch lock after {lock_elapsed:.2f} seconds - another process may be holding the lock (deadlock?)"
                logger.error(f"❌ CRITICAL: {error_msg}")
                logger.error(f"   Lock key: {dispatch_lock_key}")
                raise RuntimeError(error_msg)
        
        lock_elapsed = time.time() - lock_acquire_start
        if lock_elapsed > 1.0:
            logger.warning(f"⚠️  Lock acquisition took {lock_elapsed:.2f} seconds (slow)")
        else:
            logger.debug(f"✅ Acquired Redis dispatch lock in {lock_elapsed:.3f} seconds")

        # Load session while holding the lock
        try:
            session = load_session(session_id)
            logger.info(f"✅ Session loaded successfully")
        except Exception as load_error:
            logger.error(f"❌ CRITICAL: Failed to load session {session_id}: {load_error}")
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to load session {session_id}: {load_error}") from load_error
        
        # Check if session is already complete
        session_status = session.get("status")
        logger.info(f"   Session status: {session_status}")
        if session_status == SessionStatus.DONE:
            logger.info(f"⏭️  Session {session_id} is already DONE - no jobs to dispatch")
            return None
        
        job_plan = session.get("job_plan", [])
        if not job_plan:
            logger.info(f"ℹ️  Session {session_id} has no job_plan - no jobs to dispatch (likely a cloned/foundation session)")
            logger.info(f"   Session keys: {list(session.keys())}")
            return None  # Legitimate "no jobs" case
        
        logger.info(f"📋 Session {session_id} has {len(job_plan)} jobs in job_plan")
        # Log current state of all jobs
        for idx, job_desc in enumerate(job_plan):
            job_type = job_desc.get("job_type", "unknown")
            job_id = job_desc.get("job_id", "None")
            logger.info(f"   Job {idx}: {job_type} - job_id: {job_id}")
        
        # Find first job without a job_id
        logger.info(f"🔍 Searching for next job to dispatch (completed: {completed_job_type})...")
        
        for idx, job_desc in enumerate(job_plan):
            job_type = job_desc.get("job_type")
            job_spec = job_desc.get("spec", {})
            existing_job_id = job_desc.get("job_id")
            
            logger.info(f"   Checking job {idx}: {job_type}")
            logger.info(f"      existing_job_id: {existing_job_id}")
            
            if existing_job_id:
                # CRITICAL: Check if this job_id actually exists in Redis/Celery
                # If it's a UUID (not a Celery task ID) and doesn't exist in Redis, it's an orphaned job_id
                # from a failed dispatch. Remove it and retry.
                # load_job is imported at top of file
                job_data = load_job(existing_job_id)
                
                # Also check if it's a UUID format (8-4-4-4-12) vs Celery task ID format
                is_uuid_format = len(existing_job_id) == 36 and existing_job_id.count('-') == 4
                
                if not job_data and is_uuid_format:
                    logger.warning(f"   ⚠️  Job {idx} ({job_type}) has orphaned UUID job_id: {existing_job_id}")
                    logger.warning(f"      Job doesn't exist in Redis - this is from a failed dispatch")
                    logger.warning(f"      Removing orphaned job_id and retrying dispatch...")
                    job_plan[idx].pop("job_id", None)
                    save_session(session_id, session, exist_ok=True)
                    logger.info(f"   ✅ Removed orphaned job_id, will retry dispatch")
                    # Fall through to dispatch logic below (don't continue)
                elif job_data:
                    # Job exists in Redis - check its status
                    job_status = job_data.get('status')
                    if isinstance(job_status, JobStatus):
                        status_value = job_status.value
                    else:
                        status_value = str(job_status) if job_status else 'unknown'
                    
                    logger.info(f"   ⏭️  Job {idx} ({job_type}) already has job_id: {existing_job_id}, status: {status_value}")
                    if status_value == JobStatus.DONE.value:
                        logger.info(f"      Job is DONE - skipping (completed successfully)")
                        continue  # CRITICAL: Skip this job, don't re-dispatch!
                    elif status_value in [JobStatus.RUNNING.value, JobStatus.READY.value]:
                        # Check for JOB_ACK to detect stuck jobs
                        # BUT FIRST: Check if job actually completed (has output files)
                        job_has_output = False
                        if job_type == 'create_structured_data' and session.get('sqlite_db'):
                            job_has_output = True
                            logger.info(f"      Job has output (sqlite_db exists) - treating as complete despite {status_value} status")
                            continue
                        elif job_type == 'train_es' and session.get('embedding_space'):
                            job_has_output = True
                            logger.info(f"      Job has output (embedding_space exists) - treating as complete despite {status_value} status")
                            continue
                        elif job_type == 'train_single_predictor' and session.get('single_predictor'):
                            job_has_output = True
                            logger.info(f"      Job has output (single_predictor exists) - treating as complete despite {status_value} status")
                            continue
                        
                        # Check for JOB_ACK to detect truly stuck jobs
                        from lib.job_manager import get_job_output_path
                        try:
                            job_dir = get_job_output_path(existing_job_id, session_id, job_type)
                            job_ack = job_dir / "JOB_ACK"
                            
                            if not job_ack.exists() and not job_dir.exists():
                                logger.warning(f"      ⚠️  Job has status {status_value} but NO JOB_ACK and NO job directory!")
                                logger.warning(f"         Task was dispatched but worker never started")
                                logger.warning(f"         Job is STUCK - clearing job_id to re-dispatch")
                                job_plan[idx]['job_id'] = None
                                session['job_plan'] = job_plan
                                save_session(session_id, session, exist_ok=True)
                                logger.info(f"      ✅ Cleared stuck job_id, will re-dispatch below")
                                # Update existing_job_id so dispatch logic below works
                                existing_job_id = None
                                # Fall through to dispatch logic (don't continue)
                            else:
                                logger.info(f"      Job is {status_value} with JOB_ACK or job_dir - skipping (started/running)")
                                continue
                        except Exception as ack_check_err:
                            logger.warning(f"      ⚠️  Could not check JOB_ACK: {ack_check_err}")
                            logger.info(f"      Job is {status_value} - skipping (already dispatched/running)")
                            continue
                    else:
                        logger.info(f"      Job status is {status_value} - skipping (has job_id)")
                        continue  # Already has a job_id and it exists
                else:
                    # Job ID exists but job not in Redis - might be a Celery task ID that hasn't been saved yet
                    # Or it might be a completed job that was cleaned up from Redis
                    # Check if this is the completed_job_type - if so, it's safe to skip
                    if completed_job_type and job_type == completed_job_type:
                        logger.info(f"   ⏭️  Job {idx} ({job_type}) matches completed job type - skipping (just completed)")
                        continue
                    # Otherwise, assume it's valid and skip
                    logger.info(f"   ⏭️  Job {idx} ({job_type}) already has job_id: {existing_job_id}, skipping (not in Redis but has job_id)")
                    continue  # Already has a job_id
            
            logger.info(f"   ✅ Found job {idx} ({job_type}) without job_id - will attempt to dispatch")
            
            # Skip train_es if embedding space already exists
            if job_type == "train_es":
                embedding_space_path = session.get("embedding_space")
                foundation_model_id = session.get("foundation_model_id")
                if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                    logger.info(f"⏭️  Skipping train_es - embedding space already exists")
                    job_plan[idx]["job_id"] = "skipped-foundation-model"
                    save_session(session_id, session, exist_ok=True)
                    continue
            
            # Skip train_knn if vector_db already exists
            if job_type == "train_knn":
                vector_db_path = session.get("vector_db")
                if vector_db_path and Path(vector_db_path).exists():
                    logger.info(f"⏭️  Skipping train_knn - vector_db already exists")
                    job_plan[idx]["job_id"] = "skipped-foundation-model"
                    save_session(session_id, session, exist_ok=True)
                    continue
            
            # Dispatch will use Celery's auto-generated task ID as the job_id
            # The Celery task will use self.request.id to get its own task ID
            logger.info(f"   🚀 Dispatching job {idx} ({job_type}) - Celery will auto-generate task ID")
            
            # Get data_file for create_structured_data
            data_file = None
            if job_type == 'create_structured_data':
                input_data = session.get('input_data')
                logger.info(f"   Getting data_file for create_structured_data:")
                logger.info(f"      input_data: {input_data}")
                if input_data and not input_data.startswith('s3://'):
                    input_path = Path(input_data)
                    if input_path.is_absolute():
                        data_file = input_path
                    else:
                        data_file = config.data_dir / input_data
                    logger.info(f"      data_file: {data_file}")
                else:
                    logger.info(f"      No local input_data found (may be S3)")
            
            # Get data_file for train_es (before dispatch)
            if job_type == 'train_es' and not data_file:
                sqlite_db = session.get('sqlite_db')
                logger.info(f"   Getting data_file for train_es:")
                logger.info(f"      sqlite_db from session: {sqlite_db}")
                data_file = sqlite_db
                if data_file:
                    logger.info(f"      data_file: {data_file}")
                    path_exists = Path(data_file).exists() if data_file else False
                    logger.info(f"      data_file exists: {path_exists}")
                else:
                    logger.warning(f"      ⚠️  No sqlite_db in session - train_es may fail!")
            
            # Dispatch job
            logger.info(f"   🚀 Dispatching job {job_type} to Celery...")

            # GUARD: Check Celery worker availability before dispatching (non-blocking check)
            target_queue = None
            if job_type in ('create_structured_data', 'train_knn', 'run_clustering'):
                target_queue = 'cpu_worker'
            elif job_type in ('train_es', 'train_single_predictor'):
                target_queue = 'gpu_training'

            if target_queue:
                try:
                    # Quick check if any workers are listening to this queue (with timeout)
                    inspect = app.control.inspect(timeout=0.5)  # Very short timeout
                    active_workers = inspect.active_queues() or {}
                    workers_for_queue = []
                    for worker_name, queues in active_workers.items():
                        for queue_info in queues:
                            if queue_info.get('name') == target_queue:
                                workers_for_queue.append(worker_name)
                                break

                    if workers_for_queue:
                        logger.info(f"   ✅ Found {len(workers_for_queue)} worker(s) listening to queue '{target_queue}': {workers_for_queue}")
                    else:
                        logger.error(f"   ❌ NO WORKERS listening to queue '{target_queue}'")
                        logger.error(f"   Available workers: {list(active_workers.keys())}")
                        
                        # AUTO-RESTART: Try to start the workers via supervisorctl
                        logger.info(f"   🔧 Attempting to auto-restart workers...")
                        
                        # Map queue to supervisor service names
                        supervisor_services = []
                        if target_queue == 'cpu_worker':
                            supervisor_services = ['featrix-cpu_worker']
                        elif target_queue == 'gpu_training':
                            supervisor_services = ['featrix-gpu_training']
                        
                        workers_restarted = False
                        if supervisor_services:
                            try:
                                import subprocess
                                # Try to start the workers
                                cmd = ['supervisorctl', 'start'] + supervisor_services
                                logger.info(f"   Running: {' '.join(cmd)}")
                                result = subprocess.run(
                                    cmd,
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                
                                if result.returncode == 0:
                                    logger.info(f"   ✅ Successfully started workers: {', '.join(supervisor_services)}")
                                    logger.info(f"   Output: {result.stdout.strip()}")
                                    
                                    # Wait a moment for workers to register with broker
                                    logger.info(f"   ⏳ Waiting 3 seconds for workers to register...")
                                    time.sleep(3)
                                    
                                    # Re-check if workers are now available
                                    inspect2 = app.control.inspect(timeout=0.5)
                                    active_workers2 = inspect2.active_queues() or {}
                                    workers_for_queue2 = []
                                    for worker_name, queues in active_workers2.items():
                                        for queue_info in queues:
                                            if queue_info.get('name') == target_queue:
                                                workers_for_queue2.append(worker_name)
                                                break
                                    
                                    if workers_for_queue2:
                                        logger.info(f"   ✅ Workers now available: {workers_for_queue2}")
                                        workers_restarted = True
                                    else:
                                        logger.warning(f"   ⚠️  Workers started but not yet registered with queue '{target_queue}'")
                                        logger.warning(f"   Job will be queued and picked up when workers are ready")
                                        workers_restarted = True  # Continue anyway - workers should pick up job
                                else:
                                    logger.error(f"   ❌ Failed to start workers (exit code {result.returncode})")
                                    logger.error(f"   stdout: {result.stdout.strip()}")
                                    logger.error(f"   stderr: {result.stderr.strip()}")
                            except subprocess.TimeoutExpired:
                                logger.error(f"   ❌ supervisorctl start timed out after 10s")
                            except FileNotFoundError:
                                logger.error(f"   ❌ supervisorctl command not found")
                            except Exception as restart_err:
                                logger.error(f"   ❌ Error restarting workers: {restart_err}")
                        
                        if not workers_restarted:
                            logger.error(f"   ❌ CRITICAL: Workers could not be auto-restarted")
                            logger.error(f"   Manual intervention required:")
                            logger.error(f"      supervisorctl start {' '.join(supervisor_services)}")
                            logger.error(f"   Job will be queued in Redis but will NOT execute until workers are available")
                            # DON'T raise - let the job queue in Redis, it won't be lost
                            logger.warning(f"   ⚠️  Queueing job anyway - it will execute when workers start")
                        
                except Exception as inspect_err:
                    # Non-critical - continue with dispatch even if inspection fails
                    logger.warning(f"   ⚠️  Could not check worker availability (non-critical): {inspect_err}")
                    logger.warning(f"   Error type: {type(inspect_err).__name__}")
                    logger.debug(f"   Traceback: {traceback.format_exc()}")
                    logger.debug(f"   Continuing with dispatch - send_task will verify connection")

            try:
                # Skip broker connection verification - send_task will fail fast if Redis is down
                # This avoids the slow ensure_connection retry logic
                logger.debug(f"   🔌 Sending task to Celery (connection will be verified on send)...")
                
                # Send task to Celery (pass None as job_id, tasks will use self.request.id)
                if job_type == 'create_structured_data':
                    task = app.send_task(
                        'celery_app.create_structured_data',
                        args=[job_spec, None, str(data_file) if data_file else None, session_id],
                        queue='cpu_worker'
                    )
                elif job_type == 'pre_analysis_architecture':
                    data_file = data_file or session.get('sqlite_db')
                    strings_cache = session.get('strings_cache', '')
                    logger.info(f"   📋 pre_analysis_architecture parameters:")
                    logger.info(f"      data_file: {data_file}")
                    logger.info(f"      strings_cache: {strings_cache}")
                    logger.info(f"   📤 Sending pre_analysis_architecture task to cpu_worker queue...")
                    task = app.send_task(
                        'celery_app.pre_analysis_architecture',
                        args=[job_spec, None, session_id, str(data_file) if data_file else None, strings_cache],
                        queue='cpu_worker'  # CPU queue - quick search doesn't need GPU
                    )
                    logger.info(f"   ✅ pre_analysis_architecture task sent (task.id: {task.id})")
                elif job_type == 'train_es':
                    data_file = data_file or session.get('sqlite_db')
                    strings_cache = session.get('strings_cache', '')
                    logger.info(f"   📋 train_es parameters:")
                    logger.info(f"      data_file: {data_file}")
                    logger.info(f"      strings_cache: {strings_cache}")
                    if strings_cache:
                        logger.info(f"   🔗 Passing strings_cache to train_es: {strings_cache}")
                        # Verify the cache file exists
                        cache_path = Path(strings_cache)
                        if cache_path.exists():
                            logger.info(f"      ✅ Cache file exists: {cache_path.resolve()}")
                        else:
                            logger.warning(f"      ⚠️  Cache file does not exist: {cache_path.resolve()}")
                    else:
                        logger.warning(f"   ⚠️  No strings_cache in session - train_es will run without string cache")
                    if not data_file:
                        logger.error(f"   ❌ CRITICAL: No data_file or sqlite_db for train_es!")
                        logger.error(f"      Session sqlite_db: {session.get('sqlite_db')}")
                        logger.error(f"      This will cause train_es to fail!")
                    logger.info(f"   📤 Sending train_es task to gpu_training queue...")
                    # Pass None as job_id - the Celery task will use self.request.id
                    task = app.send_task(
                        'celery_app.train_es',
                        args=[job_spec, None, session_id, str(data_file) if data_file else None, strings_cache],
                        queue='gpu_training'
                    )
                    logger.info(f"   ✅ train_es task sent (task.id: {task.id})")
                elif job_type == 'train_knn':
                    if 'model_path' not in job_spec:
                        job_spec['model_path'] = session.get('embedding_space')
                    if 'sqlite_db_path' not in job_spec:
                        job_spec['sqlite_db_path'] = session.get('sqlite_db')
                    if 'strings_cache' not in job_spec:
                        job_spec['strings_cache'] = session.get('strings_cache')
                    task = app.send_task(
                        'celery_app.train_knn',
                        args=[job_spec, None, session_id],
                        queue='cpu_worker'
                    )
                elif job_type == 'train_single_predictor':
                    task = app.send_task(
                        'celery_app.train_single_predictor',
                        args=[job_spec, None, session_id],
                        queue='gpu_training'
                    )
                elif job_type == 'run_clustering':
                    clustering_job_spec = {
                        'model_path': session.get('embedding_space'),
                        'sqlite_db': session.get('sqlite_db'),
                        'strings_cache': session.get('strings_cache'),
                        'session_id': session_id
                    }
                    task = app.send_task(
                        'celery_app.run_clustering',
                        args=[clustering_job_spec],
                        queue='cpu_worker'
                    )
                else:
                    logger.warning(f"⚠️  Unknown job_type {job_type}, skipping")
                    continue
                
                # Skip task state verification - accessing task.state can be slow
                # send_task() will raise an exception if Redis is down, so we'll catch that
                # The task will be queued or fail fast - no need to verify state synchronously
                logger.info(f"✅ Task {task.id} sent to Celery queue '{task.queue if hasattr(task, 'queue') else 'default'}'")
                
                # Check if there are other jobs in this queue
                if target_queue:
                    try:
                        # Check how many jobs are in the queue
                        inspect = app.control.inspect(timeout=0.5)
                        reserved_tasks = inspect.reserved() or {}
                        active_tasks = inspect.active() or {}
                        
                        # Count tasks in this specific queue
                        queue_reserved_count = 0
                        queue_active_count = 0
                        
                        for worker_name, tasks in reserved_tasks.items():
                            if target_queue in worker_name or any(t.get('delivery_info', {}).get('routing_key') == target_queue for t in tasks):
                                queue_reserved_count += len(tasks)
                        
                        for worker_name, tasks in active_tasks.items():
                            if target_queue in worker_name or any(t.get('delivery_info', {}).get('routing_key') == target_queue for t in tasks):
                                queue_active_count += len(tasks)
                        
                        total_queued = queue_reserved_count + queue_active_count
                        
                        if queue_active_count > 0:
                            logger.info(f"   ⏳ QUEUE STATUS: {queue_active_count} job(s) currently RUNNING in '{target_queue}' queue")
                            logger.info(f"      → This job will WAIT until the running job(s) complete")
                            if queue_reserved_count > 0:
                                logger.info(f"      → Plus {queue_reserved_count} job(s) already waiting in queue")
                                logger.info(f"      → Your job position: #{total_queued + 1} in queue")
                        elif queue_reserved_count > 0:
                            logger.info(f"   ⏳ QUEUE STATUS: {queue_reserved_count} job(s) waiting in '{target_queue}' queue")
                            logger.info(f"      → Your job position: #{queue_reserved_count + 1} in queue")
                        else:
                            logger.info(f"   ✅ QUEUE STATUS: No other jobs in '{target_queue}' queue - will start immediately")
                    except Exception as queue_check_err:
                        logger.debug(f"   (Could not check queue status: {queue_check_err})")
                
                # CRITICAL: Update job_id to Celery task ID and save to Redis
                logger.info(f"   🔄 Setting job_id to Celery task ID {task.id}")
                job_plan[idx]["job_id"] = task.id
                save_session(session_id, session, exist_ok=True)
                logger.info(f"   ✅ Updated job_id to Celery task ID {task.id} in session")

                # Save job to Redis for tracking (ONLY save the Celery task ID, NOT the placeholder UUID)
                redis_save_success = False
                try:
                    save_job(
                        job_id=task.id,  # Use Celery task ID, NOT placeholder UUID
                        job_data={
                            'status': JobStatus.READY,
                            'created_at': datetime.now(tz=ZoneInfo("America/New_York")),
                            'job_spec': job_spec,
                        },
                        session_id=session_id,
                        job_type=job_type
                    )
                    # Verify job was actually saved to Redis
                    saved_job = load_job(task.id)
                    if saved_job:
                        redis_save_success = True
                        logger.info(f"   ✅ Job {task.id} saved to Redis and verified")
                    else:
                        logger.error(f"   ❌ CRITICAL: Job {task.id} NOT found in Redis after save")
                        logger.error(f"      save_job() succeeded but load_job() returned None")
                except Exception as redis_err:
                    logger.error(f"   ❌ CRITICAL: Failed to save job {task.id} to Redis: {redis_err}")
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                
                # CRITICAL: If Redis save failed, cleanup and raise
                if not redis_save_success:
                    logger.error(f"   🔄 Attempting to clean up failed dispatch...")
                    try:
                        # Remove task ID from job_plan so it can be retried
                        job_plan[idx]["job_id"] = None
                        save_session(session_id, session, exist_ok=True)
                        logger.info(f"   ✅ Removed task ID from job_plan to allow retry")
                        
                        # Revoke the Celery task
                        app.control.revoke(task.id, terminate=True)
                        logger.info(f"   ✅ Revoked Celery task {task.id}")
                    except Exception as cleanup_err:
                        logger.error(f"   ❌ Cleanup failed: {cleanup_err}")
                    
                    raise RuntimeError(f"Job {task.id} ({job_type}) dispatched but failed to save to Redis")
                
                dispatch_elapsed = time.time() - dispatch_start
                logger.info(f"🔵 [DISPATCH] ✅ Dispatched next job: {job_type} (task_id: {task.id}, after: {completed_job_type})")
                logger.info(f"🔵 [DISPATCH] Dispatch completed in {dispatch_elapsed:.3f} seconds")
                logger.info(f"{'='*80}\n")
                return task.id
                
            except Exception as e:
                logger.error(f"   ❌ FAILED to dispatch {job_type} job: {e}")
                logger.error(f"      Error type: {type(e).__name__}")
                logger.error(f"      Full traceback: {traceback.format_exc()}")
                # CRITICAL: Do NOT save job_id to session if dispatch failed
                # Remove the job_id we set earlier
                try:
                    if job_plan[idx].get("job_id") == job_id:
                        job_plan[idx].pop("job_id", None)
                        save_session(session_id, session, exist_ok=True)
                        logger.info(f"   ✅ Removed job_id from session (dispatch failed)")
                except Exception as cleanup_err:
                    logger.error(f"   ❌ Failed to cleanup job_id from session: {cleanup_err}")
                    logger.error(f"      Error type: {type(cleanup_err).__name__}")
                    logger.error(f"      Traceback: {traceback.format_exc()}")
                # This allows retry on next call
                return None
        
        # No more jobs to dispatch
        logger.info(f"🔵 [DISPATCH] ℹ️  No more jobs to dispatch for session {session_id}")
        logger.info(f"   Completed job type: {completed_job_type}")
        logger.info(f"   Job plan has {len(job_plan)} jobs")
        all_have_job_ids = True
        for idx, job_desc in enumerate(job_plan):
            job_type = job_desc.get("job_type", "unknown")
            job_id = job_desc.get("job_id", "None")
            has_job_id = job_id and job_id != "None"
            if not has_job_id:
                all_have_job_ids = False
                logger.info(f"     {idx}: {job_type} - NO JOB_ID")
            else:
                logger.info(f"     {idx}: {job_type} - job_id: {job_id}")
        
        if all_have_job_ids:
            logger.info(f"✅ All {len(job_plan)} jobs have been dispatched")
            logger.info(f"ℹ️  Session status will be computed dynamically from job statuses")
            # NOTE: Session status is NO LONGER STORED in session files
            # It's computed on-the-fly by compute_session_status() in session_manager.py
            # This eliminates sync bugs where job status != session status
        elif not all_have_job_ids:
            logger.warning(f"⚠️  Some jobs don't have job_ids - may need retry")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Error in dispatch_next_job_in_chain: {e}")
        logger.error(f"   Full traceback: {traceback.format_exc()}")
        raise  # Re-raise to propagate error to caller
    finally:
        # Always release the Redis lock
        if lock_acquired:
            try:
                redis_client.delete(dispatch_lock_key)
                logger.debug(f"🔓 Released Redis dispatch lock")
            except Exception as unlock_err:
                logger.error(f"❌ CRITICAL: Error releasing Redis lock: {unlock_err}")
                logger.error(f"   Error type: {type(unlock_err).__name__}")
                logger.error(f"   Lock key: {dispatch_lock_key}")
                logger.error(f"   Traceback: {traceback.format_exc()}")


def create_job_chain_for_session(session_id: str) -> Optional[str]:
    """
    Create a Celery chain for all jobs in a session's job_plan.
    
    This replaces step_session by creating a chain that executes all jobs
    in sequence automatically.
    
    Args:
        session_id: Session ID to create chain for
        
    Returns:
        First task ID in the chain, or None if no jobs to run
    """
    session = load_session(session_id)
    
    # Check if session is already complete
    session_status = session.get("status")
    if session_status == SessionStatus.DONE:
        logger.info(f"Session {session_id} is already DONE, skipping chain creation")
        return None
    
    job_plan = session.get("job_plan", [])
    if not job_plan:
        logger.info(f"Session {session_id} has no job_plan, skipping chain creation")
        return None
    
    # Build chain of tasks
    tasks = []
    job_ids = []
    
    for idx, job_desc in enumerate(job_plan):
        job_type = job_desc.get("job_type")
        job_spec = job_desc.get("spec", {})
        existing_job_id = job_desc.get("job_id")
        
        # Skip jobs that already have a job_id (already queued/completed)
        if existing_job_id:
            logger.info(f"⏭️  Skipping job {idx} ({job_type}) - already has job_id: {existing_job_id}")
            continue
        
        # Skip train_es if embedding space already exists
        if job_type == "train_es":
            embedding_space_path = session.get("embedding_space")
            foundation_model_id = session.get("foundation_model_id")
            if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                logger.info(f"⏭️  Skipping train_es - embedding space already exists")
                job_plan[idx]["job_id"] = "skipped-foundation-model"
                save_session(session_id, session, exist_ok=True)
                continue
        
        # Skip train_knn if vector_db already exists
        if job_type == "train_knn":
            vector_db_path = session.get("vector_db")
            if vector_db_path and Path(vector_db_path).exists():
                logger.info(f"⏭️  Skipping train_knn - vector_db already exists")
                job_plan[idx]["job_id"] = "skipped-foundation-model"
                save_session(session_id, session, exist_ok=True)
                continue
        
        # Generate job_id
        job_id = str(uuid4())
        job_ids.append((idx, job_id))
        
        # Get data_file for create_structured_data
        data_file = None
        if job_type == 'create_structured_data':
            input_data = session.get('input_data')
            if input_data and not input_data.startswith('s3://'):
                input_path = Path(input_data)
                if input_path.is_absolute():
                    data_file = input_path
                else:
                    data_file = config.data_dir / input_data
        
        # Create Celery task signature
        if job_type == 'create_structured_data':
            task = app.signature(
                'celery_app.create_structured_data',
                args=[job_spec, job_id, str(data_file) if data_file else None, session_id],
                queue='cpu_worker'
            )
        elif job_type == 'pre_analysis_architecture':
            # Get data_file and strings_cache from session
            data_file = data_file or session.get('sqlite_db')
            strings_cache = session.get('strings_cache', '')
            task = app.signature(
                'celery_app.pre_analysis_architecture',
                args=[job_spec, job_id, session_id, str(data_file) if data_file else None, strings_cache],
                queue='cpu_worker'
            )
        elif job_type == 'train_es':
            # Get data_file and strings_cache from session
            data_file = data_file or session.get('sqlite_db')
            strings_cache = session.get('strings_cache', '')
            task = app.signature(
                'celery_app.train_es',
                args=[job_spec, job_id, session_id, str(data_file) if data_file else None, strings_cache],
                queue='gpu_training'
            )
        elif job_type == 'train_knn':
            # Update job_spec with paths from session
            if 'model_path' not in job_spec:
                job_spec['model_path'] = session.get('embedding_space')
            if 'sqlite_db_path' not in job_spec:
                job_spec['sqlite_db_path'] = session.get('sqlite_db')
            if 'strings_cache' not in job_spec:
                job_spec['strings_cache'] = session.get('strings_cache')
            task = app.signature(
                'celery_app.train_knn',
                args=[job_spec, job_id, session_id],
                queue='cpu_worker'
            )
        elif job_type == 'train_single_predictor':
            task = app.signature(
                'celery_app.train_single_predictor',
                args=[job_spec, job_id, session_id],
                queue='gpu_training'
            )
        elif job_type == 'run_clustering':
            clustering_job_spec = {
                'model_path': session.get('embedding_space'),
                'sqlite_db': session.get('sqlite_db'),
                'strings_cache': session.get('strings_cache'),
                'session_id': session_id
            }
            task = app.signature(
                'celery_app.run_clustering',
                args=[clustering_job_spec],
                queue='cpu_worker'
            )
        else:
            logger.warning(f"⚠️  Unknown job_type {job_type}, skipping")
            continue
        
        tasks.append(task)
        logger.info(f"✅ Added {job_type} to chain (job_id: {job_id})")
    
    if not tasks:
        logger.info(f"No jobs to run for session {session_id}")
        return None
    
    # Create and execute chain
    chain_result = chain(*tasks).apply_async()
    first_task_id = chain_result.parent.id if hasattr(chain_result, 'parent') else chain_result.id
    
    # Update session with job_ids
    for idx, job_id in job_ids:
        job_plan[idx]["job_id"] = job_id
    save_session(session_id, session, exist_ok=True)
    
    logger.info(f"✅ Created Celery chain for session {session_id} with {len(tasks)} jobs (first task_id: {first_task_id})")
    return first_task_id
