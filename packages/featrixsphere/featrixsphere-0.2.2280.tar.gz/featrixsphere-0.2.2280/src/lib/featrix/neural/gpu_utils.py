#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
GPU/Device utilities with support for CUDA, MPS (Apple Silicon), and CPU.

Uses a backend pattern to provide device-agnostic GPU operations.
Each backend (NvidiaGPU, AppleGPU, NoGPU) implements the GPUBackend interface.
"""
import time
import torch
import logging
from abc import ABC, abstractmethod

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


# ============================================================================
# Backend Abstract Base Class
# ============================================================================

class GPUBackend(ABC):
    """Abstract base class for GPU/device backends."""
    
    @abstractmethod
    def get_device(self) -> torch.device:
        """Get the torch device."""
        pass
    
    @abstractmethod
    def get_device_type(self) -> str:
        """Get device type as string."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass
    
    @abstractmethod
    def get_memory_allocated(self) -> float:
        """Get allocated memory in GB."""
        pass
    
    @abstractmethod
    def get_memory_reserved(self) -> float:
        """Get reserved memory in GB."""
        pass
    
    @abstractmethod
    def get_max_memory_allocated(self) -> float:
        """Get peak allocated memory in GB."""
        pass
    
    @abstractmethod
    def get_max_memory_reserved(self) -> float:
        """Get peak reserved memory in GB."""
        pass
    
    @abstractmethod
    def empty_cache(self):
        """Clear memory cache."""
        pass
    
    @abstractmethod
    def synchronize(self):
        """Synchronize device operations."""
        pass
    
    @abstractmethod
    def reset_peak_memory_stats(self):
        """Reset peak memory statistics."""
        pass
    
    @abstractmethod
    def set_seed(self, seed: int):
        """Set random seed for device operations."""
        pass
    
    @abstractmethod
    def get_memory_summary(self, abbreviated: bool = True) -> str:
        """Get memory summary string (empty string if not supported)."""
        pass
    
    @abstractmethod
    def get_memory_snapshot(self) -> list:
        """Get memory snapshot list (empty list if not supported)."""
        pass
    
    @abstractmethod
    def get_device_properties(self, device_id: int = 0):
        """Get device properties (returns None if not supported)."""
        pass
    
    @abstractmethod
    def get_current_device_id(self) -> int:
        """Get current device ID (returns 0 if not supported)."""
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.get_device_type()})"


# ============================================================================
# CUDA Backend (NVIDIA GPUs)
# ============================================================================

class NvidiaGPU(GPUBackend):
    """NVIDIA CUDA GPU backend."""
    
    def __init__(self):
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")
        self._device = torch.device("cuda")
        logger.info("🖥️  Initialized NVIDIA CUDA GPU backend")
    
    def get_device(self) -> torch.device:
        return self._device
    
    def get_device_type(self) -> str:
        return "cuda"
    
    def is_available(self) -> bool:
        return torch.cuda.is_available()
    
    def get_memory_allocated(self) -> float:
        return torch.cuda.memory_allocated() / (1024**3)
    
    def get_memory_reserved(self) -> float:
        return torch.cuda.memory_reserved() / (1024**3)
    
    def get_max_memory_allocated(self) -> float:
        return torch.cuda.max_memory_allocated() / (1024**3)
    
    def get_max_memory_reserved(self) -> float:
        return torch.cuda.max_memory_reserved() / (1024**3)
    
    def empty_cache(self):
        torch.cuda.empty_cache()
    
    def synchronize(self):
        torch.cuda.synchronize()
    
    def reset_peak_memory_stats(self):
        torch.cuda.reset_peak_memory_stats()
    
    def set_seed(self, seed: int):
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    
    def get_memory_summary(self, abbreviated: bool = True) -> str:
        return torch.cuda.memory_summary(abbreviated=abbreviated)
    
    def get_memory_snapshot(self) -> dict:
        return torch.cuda.memory_snapshot()
    
    def get_device_properties(self, device_id: int = 0):
        return torch.cuda.get_device_properties(device_id)
    
    def get_current_device_id(self) -> int:
        return torch.cuda.current_device()


# ============================================================================
# MPS Backend (Apple Silicon GPUs)
# ============================================================================

class AppleGPU(GPUBackend):
    """Apple Metal Performance Shaders (MPS) GPU backend."""

    _BYTES_IN_GB = 1024 ** 3

    def __init__(self):
        if not getattr(torch.backends, "mps", None):
            raise RuntimeError(
                "PyTorch was not built with MPS support (torch.backends.mps is missing)."
            )
        if not torch.backends.mps.is_available():
            raise RuntimeError(
                "MPS is not available on this machine (requires Apple Silicon + MPS driver)."
            )

        self._device = torch.device("mps")
        # Track our own notion of "peak" since MPS doesn't expose it.
        self._peak_allocated_bytes = 0
        self._peak_reserved_bytes = 0

        logger.info("⚡ Initialized Apple MPS GPU backend")

    # ---- Core device info ----

    def get_device(self) -> torch.device:
        return self._device

    def get_device_type(self) -> str:
        return "mps"

    def is_available(self) -> bool:
        return torch.backends.mps.is_available()

    # ---- Internals ----

    def _bytes_to_gb(self, n: int) -> float:
        return float(n) / self._BYTES_IN_GB

    def _update_peaks(self, allocated_bytes: int, reserved_bytes: int) -> None:
        if allocated_bytes > self._peak_allocated_bytes:
            self._peak_allocated_bytes = allocated_bytes
        if reserved_bytes > self._peak_reserved_bytes:
            self._peak_reserved_bytes = reserved_bytes

    def _current_alloc_and_reserved_bytes(self) -> tuple[int, int]:
        alloc = int(torch.mps.current_allocated_memory())
        reserved = int(torch.mps.driver_allocated_memory())
        # Update peaks on every observation
        self._update_peaks(alloc, reserved)
        return alloc, reserved

    # ---- Memory API ----

    def get_memory_allocated(self) -> float:
        alloc_bytes, _ = self._current_alloc_and_reserved_bytes()
        return self._bytes_to_gb(alloc_bytes)

    def get_memory_reserved(self) -> float:
        _, reserved_bytes = self._current_alloc_and_reserved_bytes()
        return self._bytes_to_gb(reserved_bytes)

    def get_max_memory_allocated(self) -> float:
        # Our own tracked peak since backend init or last reset.
        return self._bytes_to_gb(self._peak_allocated_bytes)

    def get_max_memory_reserved(self) -> float:
        return self._bytes_to_gb(self._peak_reserved_bytes)

    # ---- Memory / execution control ----

    def empty_cache(self):
        torch.mps.empty_cache()

    def synchronize(self):
        torch.mps.synchronize()

    def reset_peak_memory_stats(self):
        """
        For CUDA this resets internal counters; for MPS we just reset our own
        tracked peaks. Semantics are close enough for dev.
        """
        self._peak_allocated_bytes = 0
        self._peak_reserved_bytes = 0

    def set_seed(self, seed: int):
        # No torch.mps.manual_seed; torch.manual_seed covers MPS.
        torch.manual_seed(seed)

    # ---- Diagnostics / reporting ----

    def get_memory_summary(self, abbreviated: bool = True) -> str:
        alloc_bytes, reserved_bytes = self._current_alloc_and_reserved_bytes()
        alloc_gb = self._bytes_to_gb(alloc_bytes)
        reserved_gb = self._bytes_to_gb(reserved_bytes)
        peak_alloc_gb = self.get_max_memory_allocated()
        peak_reserved_gb = self.get_max_memory_reserved()

        if abbreviated:
            return (
                "MPS memory: "
                f"allocated={alloc_gb:.3f} GB, "
                f"reserved={reserved_gb:.3f} GB, "
                f"peak_alloc={peak_alloc_gb:.3f} GB, "
                f"peak_reserved={peak_reserved_gb:.3f} GB"
            )
        else:
            return (
                "MPS memory summary\n"
                f"  allocated (current): {alloc_gb:.3f} GB\n"
                f"  reserved (current):  {reserved_gb:.3f} GB\n"
                f"  peak allocated:      {peak_alloc_gb:.3f} GB\n"
                f"  peak reserved:       {peak_reserved_gb:.3f} GB\n"
                "  NOTE: peaks are tracked in Python, not by MPS itself.\n"
            )

    def get_memory_snapshot(self) -> list:
        # MPS doesn't expose detailed allocation snapshots like CUDA.
        # Return empty list so consuming code can safely iterate.
        # The detailed memory info is available via get_memory_summary() instead.
        return []

    # ---- Device properties ----

    def get_device_properties(self, device_id: int = 0):
        return {
            "name": "Apple MPS",
            "index": device_id,
            "type": "mps",
            "total_memory": None,  # not exposed
        }

    def get_current_device_id(self) -> int:
        return 0

    def __repr__(self) -> str:
        return f"<AppleGPU device={self._device}>"


# ============================================================================
# CPU Backend (No GPU)
# ============================================================================

class NoGPU(GPUBackend):
    """CPU-only backend (no accelerator). Tracks system RAM instead of GPU RAM."""

    _BYTES_IN_GB = 1024 ** 3

    def __init__(self):
        self._device = torch.device("cpu")
        logger.info("💻 Initialized CPU backend (no GPU / accelerator)")

        # Track "peaks" for parity with GPU backends
        self._peak_used_ram_bytes = 0

    # ---- Core device info ----

    def get_device(self) -> torch.device:
        return self._device

    def get_device_type(self) -> str:
        return "cpu"

    def is_available(self) -> bool:
        return True

    # ---- Memory tracking (system RAM) ----

    def _bytes_to_gb(self, n: int) -> float:
        return float(n) / self._BYTES_IN_GB

    def _update_peak(self, used_bytes: int):
        if used_bytes > self._peak_used_ram_bytes:
            self._peak_used_ram_bytes = used_bytes

    def _current_ram_bytes(self) -> int:
        if psutil is None:
            return 0
        used = psutil.virtual_memory().used
        self._update_peak(used)
        return used

    def get_memory_allocated(self) -> float:
        """Return **used system RAM**, matching CUDA/MPS GB units."""
        return self._bytes_to_gb(self._current_ram_bytes())

    def get_memory_reserved(self) -> float:
        """For CPU, 'reserved' is just total RAM."""
        if psutil is None:
            return 0.0
        total = psutil.virtual_memory().total
        return self._bytes_to_gb(total)

    def get_max_memory_allocated(self) -> float:
        return self._bytes_to_gb(self._peak_used_ram_bytes)

    def get_max_memory_reserved(self) -> float:
        return self.get_memory_reserved()

    # ---- Execution / cache control ----

    def empty_cache(self):
        pass  # No CPU caching equivalent

    def synchronize(self):
        pass  # CPU ops are synchronous

    def reset_peak_memory_stats(self):
        self._peak_used_ram_bytes = 0

    def set_seed(self, seed: int):
        torch.manual_seed(seed)

    # ---- Diagnostics ----

    def get_memory_summary(self, abbreviated: bool = True) -> str:
        if psutil is None:
            return "CPU RAM: psutil not available"
        
        vm = psutil.virtual_memory()
        used = self._bytes_to_gb(vm.used)
        avail = self._bytes_to_gb(vm.available)
        total = self._bytes_to_gb(vm.total)
        peak = self.get_max_memory_allocated()

        if abbreviated:
            return (
                f"CPU RAM: used={used:.3f} GB, available={avail:.3f} GB, peak={peak:.3f} GB"
            )
        else:
            return (
                "CPU RAM summary\n"
                f"  used:      {used:.3f} GB\n"
                f"  available: {avail:.3f} GB\n"
                f"  total:     {total:.3f} GB\n"
                f"  peak used: {peak:.3f} GB\n"
            )

    def get_memory_snapshot(self) -> list:
        # Return list with single summary dict for compatibility with consuming code
        # (which expects a list of allocation dicts like CUDA provides)
        if psutil is None:
            return []
        
        vm = psutil.virtual_memory()
        return [{
            "backend": "cpu",
            "used_bytes": vm.used,
            "available_bytes": vm.available,
            "total_bytes": vm.total,
            "used_gb": self._bytes_to_gb(vm.used),
            "available_gb": self._bytes_to_gb(vm.available),
            "total_gb": self._bytes_to_gb(vm.total),
            "peak_used_gb": self.get_max_memory_allocated(),
        }]

    # ---- Device props ----

    def get_device_properties(self, device_id: int = 0):
        if psutil is None:
            return {
                "name": "CPU",
                "index": device_id,
                "type": "cpu",
                "total_memory_gb": None,
            }
        
        vm = psutil.virtual_memory()
        return {
            "name": "CPU",
            "index": device_id,
            "type": "cpu",
            "total_memory_gb": self._bytes_to_gb(vm.total),
        }

    def get_current_device_id(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "<NoGPU device=cpu>"


# ============================================================================
# Backend Factory & Global Instance
# ============================================================================

def _detect_backend() -> GPUBackend:
    """Auto-detect and create the appropriate GPU backend."""
    if torch.cuda.is_available():
        return NvidiaGPU()
    elif torch.backends.mps.is_available():
        return AppleGPU()
    else:
        return NoGPU()


# Global backend instance
_backend: GPUBackend = None


def _get_backend() -> GPUBackend:
    """Get the current backend, initializing if needed."""
    global _backend
    if _backend is None:
        _backend = _detect_backend()
    return _backend


def set_backend_cpu():
    """Force CPU backend."""
    global _backend
    _backend = NoGPU()


def set_backend_gpu():
    """Force GPU backend (CUDA or MPS)."""
    global _backend
    if torch.cuda.is_available():
        _backend = NvidiaGPU()
    elif torch.backends.mps.is_available():
        _backend = AppleGPU()
    else:
        raise RuntimeError("No GPU available. Cannot set GPU backend.")


def reset_backend():
    """Reset to auto-detected backend."""
    global _backend
    _backend = _detect_backend()


# ============================================================================
# Public API - delegates to current backend
# ============================================================================

def get_device() -> torch.device:
    """Get the current torch device."""
    return _get_backend().get_device()


def get_device_type() -> str:
    """Get device type as string ('cuda', 'mps', or 'cpu')."""
    return _get_backend().get_device_type()


def is_gpu_available() -> bool:
    """Check if any GPU (CUDA or MPS) is available."""
    backend = _get_backend()
    return backend.is_available() and backend.get_device_type() != "cpu"


def is_cuda_available() -> bool:
    """Check if CUDA GPU is available."""
    return torch.cuda.is_available()


def is_mps_available() -> bool:
    """Check if MPS (Apple Silicon) GPU is available."""
    return torch.backends.mps.is_available()


def get_gpu_memory_allocated() -> float:
    """Get allocated GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_memory_allocated()


def get_gpu_memory_reserved() -> float:
    """Get reserved GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_memory_reserved()


def get_max_gpu_memory_allocated() -> float:
    """Get peak allocated GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_max_memory_allocated()


def get_max_gpu_memory_reserved() -> float:
    """Get peak reserved GPU memory in GB (0.0 if not supported)."""
    return _get_backend().get_max_memory_reserved()


def empty_gpu_cache():
    """Clear GPU memory cache (no-op if not supported)."""
    _get_backend().empty_cache()


def synchronize_gpu():
    """Synchronize GPU operations (no-op if not supported)."""
    _get_backend().synchronize()


def reset_gpu_peak_memory_stats():
    """Reset GPU peak memory statistics (no-op if not supported)."""
    _get_backend().reset_peak_memory_stats()


def set_gpu_seed(seed: int):
    """Set random seed for GPU operations."""
    _get_backend().set_seed(seed)


def get_gpu_memory_summary(abbreviated: bool = True) -> str:
    """Get GPU memory summary string (empty string if not supported)."""
    return _get_backend().get_memory_summary(abbreviated=abbreviated)


def get_gpu_memory_snapshot() -> dict:
    """Get GPU memory snapshot dict (empty dict if not supported)."""
    return _get_backend().get_memory_snapshot()


def get_gpu_device_properties(device_id: int = 0):
    """Get GPU device properties (returns None if not supported)."""
    return _get_backend().get_device_properties(device_id)


def get_gpu_current_device_id() -> int:
    """Get current GPU device ID (returns 0 if not supported)."""
    return _get_backend().get_current_device_id()


def get_backend_name() -> str:
    """Get the name of the current backend."""
    return _get_backend().__class__.__name__


def get_gpu_device_properties(device_id: int = 0):
    """Get GPU device properties (returns None if not supported)."""
    return _get_backend().get_device_properties(device_id)


def get_gpu_current_device_id() -> int:
    """Get current GPU device ID (returns 0 if not supported)."""
    return _get_backend().get_current_device_id()


def move_to_cpu_if_needed(tensor: torch.Tensor, detach: bool = True) -> torch.Tensor:
    """
    Move tensor to CPU if it's on a GPU device (CUDA, MPS, etc.).
    
    Args:
        tensor: PyTorch tensor (may be on any device)
        detach: If True, detach from computation graph before moving
        
    Returns:
        Tensor on CPU (or original tensor if already on CPU)
    """
    if tensor.device.type != 'cpu':
        if detach:
            return tensor.detach().cpu()
        else:
            return tensor.cpu()
    else:
        if detach:
            return tensor.detach()
        else:
            return tensor


def compare_gpu_cpu_speed(
    operation_fn,
    input_data,
    num_iterations: int = 10,
    warmup_iterations: int = 3
) -> dict:
    """
    Compare GPU vs CPU speed for a given operation.
    
    Args:
        operation_fn: Function that takes input_data and performs the operation
                     Should accept a device parameter: operation_fn(input_data, device)
        input_data: Input data for the operation (will be moved to appropriate device)
        num_iterations: Number of iterations to run for timing (default: 10)
        warmup_iterations: Number of warmup iterations before timing (default: 3)
    
    Returns:
        dict with keys:
            - 'gpu_time': Average time per iteration on GPU (seconds), or None if GPU unavailable
            - 'cpu_time': Average time per iteration on CPU (seconds)
            - 'speedup': GPU speedup ratio (gpu_time / cpu_time), or None if GPU unavailable
            - 'faster_device': 'gpu' or 'cpu' or None
            - 'gpu_available': bool
    """

    
    results = {
        'gpu_time': None,
        'cpu_time': None,
        'speedup': None,
        'faster_device': None,
        'gpu_available': is_gpu_available()
    }
    
    # Benchmark CPU
    try:
        cpu_times = []
        for i in range(warmup_iterations + num_iterations):
            start = time.time()
            operation_fn(input_data, torch.device('cpu'))
            if i >= warmup_iterations:
                cpu_times.append(time.time() - start)
        results['cpu_time'] = sum(cpu_times) / len(cpu_times)
    except Exception as e:
        logger.error(f"CPU benchmark failed: {e}")
        return results
    
    # Benchmark GPU if available
    if results['gpu_available']:
        try:
            device = get_device()
            gpu_times = []
            for i in range(warmup_iterations + num_iterations):
                start = time.time()
                operation_fn(input_data, device)
                if device.type == 'cuda':
                    torch.cuda.synchronize()
                elif device.type == 'mps':
                    # MPS doesn't have explicit sync, but we can wait a bit
                    import time as time_module
                    time_module.sleep(0.001)  # Small delay to ensure completion
                if i >= warmup_iterations:
                    gpu_times.append(time.time() - start)
            results['gpu_time'] = sum(gpu_times) / len(gpu_times)
            
            # Calculate speedup
            if results['cpu_time'] > 0:
                results['speedup'] = results['cpu_time'] / results['gpu_time']
                results['faster_device'] = 'gpu' if results['speedup'] > 1.0 else 'cpu'
            else:
                results['faster_device'] = 'gpu'
        except Exception as e:
            logger.error(f"GPU benchmark failed: {e}")
            results['gpu_available'] = False
    
    # If GPU not available or failed, CPU is the only option
    if results['gpu_time'] is None:
        results['faster_device'] = 'cpu'
    
    return results


# Convenience aliases for backward compatibility
set_device_cpu = set_backend_cpu
set_device_gpu = set_backend_gpu
reset_device = reset_backend

# Initialize backend on import
_backend = _detect_backend()

