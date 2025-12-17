from pathlib import Path

import structlog
from funasr import AutoModel
from recallia import config

logger = structlog.get_logger(__name__)


class ASRService:
    """Wrap FunASR model loading and inference."""

    def __init__(self) -> None:
        logger.info('asr_loading')
        self.model = AutoModel(
            model='paraformer-zh',
            model_revision='v2.0.4',
            vad_model='fsmn-vad',
            punc_model='ct-punc',
            spk_model='cam++',
            device=config.ASR_DEVICE,
            disable_update=True,
        )
        logger.info('asr_ready')

    def transcribe(self, file_path: Path) -> tuple[str, list[dict]]:
        """Run ASR and return transcript text and sentence-level segments."""
        result = self.model.generate(
            input=str(file_path),
            batch_size_s=300,
            hotword='王一航',
            merge_vad=True,
            merge_thr=1.0,
        )
        transcript_text, segments = self._format_result(result)
        preview = transcript_text[:300] + \
            ('...' if len(transcript_text) > 300 else '')
        logger.info(
            'asr_finished',
            chars=len(transcript_text),
            segments=len(segments),
            transcript_preview=preview,
        )
        return transcript_text, segments

    @staticmethod
    def _format_result(result) -> tuple[str, list[dict]]:
        if not result or 'sentence_info' not in result[0]:
            text = result[0]['text'] if result else ''
            return text, [{'speaker': None, 'text': text, 'start_time': None, 'end_time': None, 'emotion': None}]

        lines = []
        segments: list[dict] = []
        current_speaker = None
        buffer: list[str] = []
        for item in result[0]['sentence_info']:
            spk = item.get('spk', 0)
            text = item.get('text', '')
            start_time = item.get('start')
            end_time = item.get('end')
            segments.append(
                {
                    'speaker': f"Speaker {spk}",
                    'text': text,
                    'start_time': start_time,
                    'end_time': end_time,
                    'emotion': None,
                },
            )

            if spk == current_speaker:
                buffer.append(text)
            else:
                if buffer:
                    lines.append(
                        f"Speaker {current_speaker}: {''.join(buffer)}",
                    )
                current_speaker = spk
                buffer = [text]

        if buffer:
            lines.append(f"Speaker {current_speaker}: {''.join(buffer)}")

        return '\n'.join(lines), segments
