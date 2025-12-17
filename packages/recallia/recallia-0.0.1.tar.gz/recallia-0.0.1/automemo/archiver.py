import json
import shutil
import time
from datetime import datetime
from pathlib import Path

import structlog
from recallia import config

logger = structlog.get_logger(__name__)


class Archiver:
    """Persist artifacts per file under archive/YYYY-MM-DD/<content-hash>/."""

    def _target_dir(self, content_hash: str) -> Path:
        today = datetime.now().strftime('%Y-%m-%d')
        name_hash = content_hash[:12]
        target_dir = config.ARCHIVE_DIR / today / name_hash
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def archive(
        self,
        file_path: Path,
        transcript_text: str,
        segments: list[dict],
        summary_meta: dict,
        emotion_meta: dict,
        summary: str,
        tags: str,
        duration_sec: float,
        content_hash: str,
    ) -> str:
        target_dir = self._target_dir(content_hash)
        archived_file = self._move_original(file_path, target_dir)
        self._write_transcript_jsonl(target_dir, transcript_text, segments)
        self._write_json(target_dir / 'llm_summary.json', summary_meta)
        self._write_json(target_dir / 'llm_emotion.json', emotion_meta)
        self._write_run_log(
            target_dir,
            status='success',
            summary=summary,
            tags=tags,
            duration_sec=duration_sec,
            archived_file=str(archived_file),
            content_hash=content_hash,
        )
        logger.info('file_archived', target=str(archived_file))
        return str(archived_file)

    def mark_failure(self, archived_file: Path, error: str, content_hash: str) -> None:
        target_dir = archived_file.parent
        self._write_json(target_dir / 'error.json', {'error': error})
        self._write_run_log(
            target_dir,
            status='failed',
            summary=None,
            tags=None,
            duration_sec=None,
            archived_file=str(archived_file),
            error=error,
            content_hash=content_hash,
        )
        logger.warning(
            'file_marked_failed', target=str(
                archived_file,
            ), error=error,
        )

    def archive_failure(self, file_path: Path, error: str, content_hash: str) -> str:
        target_dir = self._target_dir(content_hash)
        archived_file = self._move_original(file_path, target_dir)
        self._write_json(target_dir / 'error.json', {'error': error})
        self._write_run_log(
            target_dir,
            status='failed',
            summary=None,
            tags=None,
            duration_sec=None,
            archived_file=str(archived_file),
            error=error,
            content_hash=content_hash,
        )
        logger.warning(
            'file_archived_with_error',
            target=str(archived_file), error=error,
        )
        return str(archived_file)

    def archive_duplicate(self, file_path: Path, existing_audio_id: int, content_hash: str) -> str:
        target_dir = self._target_dir(content_hash)
        archived_file = self._move_original(file_path, target_dir)
        self._write_run_log(
            target_dir,
            status='duplicate',
            summary=None,
            tags=None,
            duration_sec=None,
            archived_file=str(archived_file),
            duplicate_of=existing_audio_id,
            content_hash=content_hash,
        )
        logger.info(
            'file_marked_duplicate', target=str(
                archived_file,
            ), duplicate_of=existing_audio_id,
        )
        return str(archived_file)

    @staticmethod
    def _move_original(file_path: Path, target_dir: Path) -> Path:
        target_path = target_dir / file_path.name
        if target_path.exists():
            timestamp = int(time.time())
            target_path = target_dir / \
                f"{file_path.stem}_{timestamp}{file_path.suffix}"
        shutil.move(str(file_path), target_path)
        return target_path

    @staticmethod
    def _write_transcript_jsonl(target_dir: Path, transcript_text: str, segments: list[dict]) -> None:
        path = target_dir / 'transcript.jsonl'
        with path.open('w', encoding='utf-8') as f:
            f.write(
                json.dumps(
                    {'type': 'full_text', 'text': transcript_text}, ensure_ascii=False,
                ) + '\n',
            )
            for segment in segments:
                payload = {'type': 'segment', **segment}
                f.write(json.dumps(payload, ensure_ascii=False) + '\n')

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        with path.open('w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _write_run_log(
        target_dir: Path,
        status: str,
        summary: str | None,
        tags: str | None,
        duration_sec: float | None,
        archived_file: str,
        error: str | None = None,
        duplicate_of: int | None = None,
        content_hash: str | None = None,
    ) -> None:
        log_path = target_dir / 'run.log'
        lines = [
            f"status: {status}",
            f"archived_file: {archived_file}",
            f"content_hash: {content_hash}",
            f"summary: {summary}",
            f"tags: {tags}",
            f"duration_sec: {duration_sec}",
        ]
        if error:
            lines.append(f"error: {error}")
        if duplicate_of is not None:
            lines.append(f"duplicate_of: {duplicate_of}")
        log_path.write_text('\n'.join(lines), encoding='utf-8')
