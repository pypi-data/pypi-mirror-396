import os
import time
from pathlib import Path

import structlog
from recallia.archiver import Archiver
from recallia.asr_service import ASRService
from recallia.db import Database
from recallia.summarizer import Summarizer
from recallia.utils import sha256_file

logger = structlog.get_logger(__name__)


class LifeRecorderPipeline:
    """End-to-end pipeline: ASR -> summary -> archive -> persist."""

    def __init__(self, db: Database, asr: ASRService, summarizer: Summarizer, archiver: Archiver):
        self.db = db
        self.asr = asr
        self.summarizer = summarizer
        self.archiver = archiver

    def process_one_file(self, file_path: Path) -> None:
        logger.info('process_start', file=file_path.name)
        start_time = time.time()

        content_hash = sha256_file(file_path)
        existing = self.db.find_audio_by_hash(content_hash)
        if existing:
            logger.info(
                'duplicate_detected',
                file=file_path.name,
                content_hash=content_hash,
                audio_id=existing['id'],
            )
            self.archiver.archive_duplicate(
                file_path, existing['id'], content_hash,
            )
            return

        archive_path = None
        try:
            transcript_text, segments = self.asr.transcribe(file_path)
            segments, emotion_meta = self.summarizer.label_emotions(segments)
            summary, tags, summary_meta = self.summarizer.summarize(
                transcript_text,
            )

            duration = time.time() - start_time
            archive_path = self.archiver.archive(
                file_path=file_path,
                transcript_text=transcript_text,
                segments=segments,
                summary_meta=summary_meta,
                emotion_meta=emotion_meta,
                summary=summary,
                tags=tags,
                duration_sec=round(duration, 3),
                content_hash=content_hash,
            )
            file_size_mb = round(
                os.path.getsize(
                    archive_path,
                ) / 1024 / 1024, 2,
            )

            audio_id = self.db.insert_audio_file(
                original_filename=file_path.name,
                archive_path=archive_path,
                file_size_mb=file_size_mb,
                duration_sec=None,
                summary=summary,
                tags=tags,
                content_hash=content_hash,
            )
            self.db.insert_transcript_segments(audio_id, segments)

            logger.info(
                'process_done',
                file=file_path.name,
                seconds=round(duration, 1),
                summary_preview=summary[:200],
                tags=tags,
            )
        except Exception as exc:
            logger.error(
                'process_failed', file=file_path.name,
                error=str(exc), exc_info=True,
            )
            if archive_path:
                self.archiver.mark_failure(
                    Path(archive_path), str(exc), content_hash,
                )
            else:
                self.archiver.archive_failure(
                    file_path, str(exc), content_hash,
                )
