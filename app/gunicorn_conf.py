import multiprocessing
import os


# GUNICORN_WORKERS_PER_CORE = 1.0
# GUNICORN_MAX_WORKERS = 4
# GUNICORN_LOG_LEVEL = info
# GUNICORN_GRACEFUL_TIMEOUT = 600
# GUNICORN_TIMEOUT = 1200
# GUNICORN_KEEP_ALIVE = 6
# HOST = 0.0.0.0
# PORT = 8000
# PUBLIC_PATH = ""

WORKERS_PER_CORE = float(os.getenv("GUNICORN_WORKERS_PER_CORE", "1"))
MAX_WORKERS = int(os.getenv("GUNICORN_MAX_WORKERS", "1"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


def get_workers_count(max_workers: int, workers_per_core: float) -> int:
    cores = multiprocessing.cpu_count()
    default_web_concurrency = workers_per_core * cores
    web_concurrency = max(int(default_web_concurrency), 2)
    if max_workers:
        web_concurrency = min(web_concurrency, max_workers)
    return web_concurrency


# Gunicorn config variables
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
workers = get_workers_count(max_workers=MAX_WORKERS, workers_per_core=WORKERS_PER_CORE)
bind = f"{HOST}:{PORT}"
# worker_tmp_dir = "/dev/shm"
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "600"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "1200"))
keepalive = int(os.getenv("GUNICORN_KEEP_ALIVE", "5"))
worker_class = "uvicorn.workers.UvicornWorker"
