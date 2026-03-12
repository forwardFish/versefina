from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from jobs.daily_loop import job_name
except ImportError:  # pragma: no cover - supports python -m apps.worker.src.main
    from .jobs.daily_loop import job_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_worker_manifest() -> dict[str, str]:
    return {
        "service": "versefina-worker",
        "mode": "standalone",
        "primary_job": job_name(),
    }


def placeholder_task() -> dict[str, str]:
    logger.info("Worker 占位任务开始执行...")
    time.sleep(2)
    logger.info("Worker 占位任务执行完成！")
    return {"status": "done"}


if __name__ == "__main__":  # pragma: no cover - manual startup path
    logger.info("VerseFina Worker 启动成功 (Standalone Mode)")
    try:
        while True:
            placeholder_task()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Worker 停止")
