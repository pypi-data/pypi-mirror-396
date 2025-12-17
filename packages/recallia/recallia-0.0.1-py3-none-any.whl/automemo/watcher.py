import time
from pathlib import Path

import structlog
from recallia.pipeline import LifeRecorderPipeline
from watchdog.events import FileSystemEventHandler

logger = structlog.get_logger(__name__)


class InboxHandler(FileSystemEventHandler):
    """Watch inbox for new audio files and trigger processing."""

    def __init__(self, pipeline: LifeRecorderPipeline):
        self.pipeline = pipeline

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if file_path.suffix.lower() not in ['.mp3', '.wav', '.m4a']:
            return

        time.sleep(2)  # naive debounce
        logger.info('file_detected', file=file_path.name)
        self.pipeline.process_one_file(file_path)
