import time
import os
import psutil
import numpy as np

class RuntimeProfiler:
    """
    Profiles inference execution time and memory footprint on CPU/GPU.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def measure_memory_mb(self):
        """Returns resident memory in megabytes (RSS)."""
        return self.process.memory_info().rss / (1024 * 1024)

    def benchmark_latency(self, infer_fn, n_warmup=5, n_runs=30):
        """
        Executes warmup runs followed by benchmark iterations.
        Returns detailed summary: mean, std, p50, p95, p99 (ms).
        """
        for _ in range(n_warmup):
            infer_fn()
            
        times_ms = []
        mem_start = self.measure_memory_mb()
        
        for _ in range(n_runs):
            t0 = time.perf_counter()
            infer_fn()
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            times_ms.append(elapsed_ms)
            
        mem_end = self.measure_memory_mb()
        
        return {
            "n_runs": n_runs,
            "mean_ms": round(float(np.mean(times_ms)), 2),
            "std_ms": round(float(np.std(times_ms)), 2),
            "p50_ms": round(float(np.percentile(times_ms, 50)), 2),
            "p95_ms": round(float(np.percentile(times_ms, 95)), 2),
            "p99_ms": round(float(np.percentile(times_ms, 99)), 2),
            "min_ms": round(float(np.min(times_ms)), 2),
            "max_ms": round(float(np.max(times_ms)), 2),
            "resident_mem_mb": round(mem_end, 2),
            "mem_delta_mb": round(mem_end - mem_start, 2)
        }
