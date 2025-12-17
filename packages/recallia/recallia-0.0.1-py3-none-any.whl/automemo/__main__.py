import time
from pathlib import Path

from recallia import config
from recallia.archiver import Archiver
from recallia.asr_service import ASRService
from recallia.db import Database
from recallia.logging_config import configure_logging
from recallia.pipeline import LifeRecorderPipeline
from recallia.summarizer import Summarizer
from recallia.watcher import InboxHandler
from watchdog.observers import Observer


def scan_backlog(pipeline: LifeRecorderPipeline, inbox_dir: Path) -> None:
    """Process any audio files already present in inbox on startup."""
    for file_path in inbox_dir.glob('*'):
        if file_path.suffix.lower() in ['.mp3', '.wav', '.m4a']:
            pipeline.process_one_file(file_path)


def main() -> None:
    config.ensure_directories()
    logger = configure_logging(config.LOG_DIR)
    logger.info('startup', inbox=str(config.INBOX_DIR))

    db = Database(config.DB_PATH)
    asr = ASRService()
    summarizer = Summarizer()
    archiver = Archiver()
    pipeline = LifeRecorderPipeline(
        db=db, asr=asr, summarizer=summarizer, archiver=archiver,
    )

    scan_backlog(pipeline, config.INBOX_DIR)

    observer = Observer()
    observer.schedule(
        InboxHandler(pipeline), str(
            config.INBOX_DIR,
        ), recursive=False,
    )
    observer.start()
    logger.info('watcher_started', inbox=str(config.INBOX_DIR))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
