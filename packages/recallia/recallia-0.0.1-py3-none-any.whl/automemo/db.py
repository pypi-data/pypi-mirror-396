import sqlite3
from collections.abc import Iterable
from collections.abc import Mapping
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class Database:
    """Thin wrapper around SQLite with migrations for audio + transcript tables."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys = ON')
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audio_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                archive_path TEXT NOT NULL,
                file_size_mb REAL,
                duration_sec REAL,
                summary TEXT,
                tags TEXT,
                content_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
            """,
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transcript_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audio_file_id INTEGER NOT NULL,
                speaker TEXT,
                text TEXT NOT NULL,
                start_time REAL,
                end_time REAL,
                emotion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(audio_file_id) REFERENCES audio_files(id) ON DELETE CASCADE
            )
            """,
        )

        self._ensure_column('audio_files', 'content_hash', 'TEXT')
        self.conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_audio_content_hash
            ON audio_files(content_hash) WHERE content_hash IS NOT NULL
            """,
        )
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_transcript_audio ON transcript_segments(audio_file_id)',
        )
        self.conn.commit()
        logger.info('db_schema_ready', db_path=str(self.db_path))

    def _ensure_column(self, table: str, column: str, col_type: str) -> None:
        cols = {
            row[1]
            for row in self.conn.execute(f'PRAGMA table_info({table})')
        }
        if column not in cols:
            self.conn.execute(
                f'ALTER TABLE {table} ADD COLUMN {column} {col_type}',
            )

    def insert_audio_file(
        self,
        original_filename: str,
        archive_path: str,
        file_size_mb: float,
        duration_sec: float | None,
        summary: str,
        tags: str,
        content_hash: str,
    ) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO audio_files (original_filename, archive_path, file_size_mb, duration_sec, summary, tags, content_hash, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                original_filename, archive_path,
                file_size_mb, duration_sec, summary, tags, content_hash,
            ),
        )
        self.conn.commit()
        audio_id = cursor.lastrowid
        assert audio_id is not None  # lastrowid is set for INSERT rows
        audio_int = int(audio_id)
        logger.info(
            'db_audio_inserted', audio_id=audio_int,
            archive_path=archive_path,
        )
        return audio_int

    def insert_transcript_segments(self, audio_file_id: int, segments: Iterable[Mapping]) -> None:
        payload = [
            (
                audio_file_id,
                segment.get('speaker'),
                segment.get('text'),
                segment.get('start_time'),
                segment.get('end_time'),
                segment.get('emotion'),
            )
            for segment in segments
        ]
        self.conn.executemany(
            """
            INSERT INTO transcript_segments (audio_file_id, speaker, text, start_time, end_time, emotion)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        self.conn.commit()
        logger.info(
            'db_segments_inserted',
            audio_file_id=audio_file_id, count=len(payload),
        )

    def close(self) -> None:
        self.conn.close()

    def find_audio_by_hash(self, content_hash: str) -> sqlite3.Row | None:
        cur = self.conn.execute(
            'SELECT id, archive_path FROM audio_files WHERE content_hash = ? LIMIT 1',
            (content_hash,),
        )
        return cur.fetchone()
