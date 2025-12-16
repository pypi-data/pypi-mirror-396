#!/usr/bin/env python3
"""
Query Schema Worker - Processes LLM schema analysis jobs from Redis queue.

Watches query-schema-queue in Redis, processes jobs with 60s timeout,
stores results in /tmp/query-schema-jobs/job_{uuid}.json

Run as systemd service for automatic restart on failure.
"""

import json
import logging
import signal
import sys
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] %(name)-30s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/featrix/query-schema-worker.log')
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle SIGTERM/SIGINT for graceful shutdown."""
    global shutdown_requested
    logger.info(f"🛑 Received signal {signum} - shutting down gracefully...")
    shutdown_requested = True


def process_job(job_id: str) -> bool:
    """
    Process a single schema analysis job.
    
    Args:
        job_id: UUID of the job to process
    
    Returns:
        True if job completed successfully, False otherwise
    """
    job_file = Path(f"/tmp/query-schema-jobs/job_{job_id}.json")
    
    if not job_file.exists():
        logger.error(f"❌ Job file not found: {job_file}")
        return False
    
    try:
        # Load job data
        with open(job_file, 'r') as f:
            job_data = json.load(f)
        
        logger.info(f"🔄 Processing job {job_id} ({len(job_data['columns'])} columns)")
        
        # Update status to processing
        job_data["status"] = "processing"
        job_data["started_at"] = time.time()
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        # Call LLM API with timeout
        import requests
        
        api_url = "https://api.openai.com/v1/chat/completions"
        
        # Get OpenAI API key from environment
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        # Build prompt
        system_prompt = (
            "You are an expert data analyst. Analyze the given column names and respond "
            "with a valid JSON object containing detected patterns and relationships."
        )
        
        user_message = f"{job_data['question']}\n\nColumns: {json.dumps(job_data['columns'])}"
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"   📡 Calling OpenAI API (timeout=60s)...")
        start_time = time.time()
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=60  # 60 second timeout
        )
        
        elapsed = time.time() - start_time
        logger.info(f"   ✅ API call completed in {elapsed:.2f}s")
        
        if response.status_code == 200:
            api_result = response.json()
            content = api_result["choices"][0]["message"]["content"]
            
            # Parse JSON from LLM response
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            result = json.loads(content)
            
            # Update job with result
            job_data["status"] = "completed"
            job_data["completed_at"] = time.time()
            job_data["runtime_seconds"] = round(elapsed, 2)
            job_data["result"] = result
            job_data["error"] = None
            
            logger.info(f"✅ Job {job_id} completed successfully (runtime: {elapsed:.2f}s)")
            
        else:
            error_msg = f"OpenAI API returned {response.status_code}: {response.text[:200]}"
            logger.error(f"❌ Job {job_id} failed: {error_msg}")
            
            job_data["status"] = "failed"
            job_data["completed_at"] = time.time()
            job_data["runtime_seconds"] = round(elapsed, 2)
            job_data["error"] = error_msg
        
        # Save final job state
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return job_data["status"] == "completed"
        
    except requests.exceptions.Timeout:
        error_msg = "API request timeout (60s exceeded)"
        logger.error(f"❌ Job {job_id} failed: {error_msg}")
        
        job_data["status"] = "failed"
        job_data["completed_at"] = time.time()
        job_data["runtime_seconds"] = 60.0
        job_data["error"] = error_msg
        
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return False
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"❌ Job {job_id} failed: {error_msg}")
        logger.exception(e)
        
        job_data["status"] = "failed"
        job_data["completed_at"] = time.time()
        job_data["runtime_seconds"] = time.time() - job_data.get("started_at", time.time())
        job_data["error"] = error_msg
        
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return False


def main():
    """Main worker loop - polls Redis queue and processes jobs."""
    import redis
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("🚀 Query Schema Worker started")
    logger.info("   Queue: query-schema-queue")
    logger.info("   Timeout: 60s per job")
    logger.info("   Storage: /tmp/query-schema-jobs/")
    
    # Ensure job directory exists
    Path("/tmp/query-schema-jobs").mkdir(parents=True, exist_ok=True)
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Test Redis connection
    try:
        r.ping()
        logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.error(f"❌ Cannot connect to Redis: {e}")
        sys.exit(1)
    
    processed_count = 0
    
    while not shutdown_requested:
        try:
            # Block for 1 second waiting for job (BLPOP)
            result = r.blpop("query-schema-queue", timeout=1)
            
            if result is None:
                # Timeout - no job available, continue loop
                continue
            
            queue_name, job_id = result
            logger.info(f"📥 Received job {job_id} from queue")
            
            # Process the job
            success = process_job(job_id)
            processed_count += 1
            
            if success:
                logger.info(f"   Job {job_id} processed successfully (total: {processed_count})")
            else:
                logger.warning(f"   Job {job_id} failed (total: {processed_count})")
            
        except redis.exceptions.ConnectionError as e:
            logger.error(f"❌ Redis connection error: {e}")
            logger.info("   Retrying in 5 seconds...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt - shutting down...")
            break
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in worker loop: {e}")
            logger.exception(e)
            time.sleep(1)  # Brief pause before retry
    
    logger.info(f"👋 Query Schema Worker stopped (processed {processed_count} jobs)")


if __name__ == "__main__":
    main()
