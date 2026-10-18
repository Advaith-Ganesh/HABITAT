"""Resource-bounded subprocess execution, no persistent raw document storage."""
import subprocess
import sys
import threading
import time
from backend.document_analysis import Analysis, MAX_BYTES

_slots=threading.BoundedSemaphore(2)

def process_pdf(data,category,baseline=False):
    if len(data)>MAX_BYTES:raise ValueError('PDF exceeds 2 MiB limit')
    if not _slots.acquire(blocking=False):raise RuntimeError('Document processing busy; retry later')
    started=time.perf_counter()
    try:
        run=subprocess.run([sys.executable,'-m','backend.document_worker',category]+(['baseline'] if baseline else []),
                           input=data,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=6)
        if run.returncode:
            raise ValueError('PDF rejected: invalid, encrypted, unmarked, unsupported or resource-limited. Use a marked synthetic PDF, at most 2 MiB and 5 pages.')
        result=Analysis.model_validate_json(run.stdout)
        result.processing_ms=round((time.perf_counter()-started)*1000,3)
        return result.model_dump()
    except (subprocess.TimeoutExpired, MemoryError):
        raise ValueError('PDF parsing exceeded resource limits; manual review is required')
    finally:_slots.release()
