import json

import ollama
import structlog
from recallia import config

logger = structlog.get_logger(__name__)


class Summarizer:
    """LLM wrapper for summary, tags, and lightweight emotion labeling."""

    def summarize(self, transcript: str) -> tuple[str, str, dict]:
        if len(transcript) < 10:
            return 'Too short to summarize', 'none', {
                'prompt': None,
                'response': None,
            }

        prompt = f"""
You are an assistant. Read the transcript and return JSON with:
1. "summary": concise Chinese summary.
2. "tags": 3-5 keywords separated by commas.
Transcript:
{transcript[:3000]}
""".strip()

        try:
            client = ollama.Client(host=config.OLLAMA_HOST)
            response = client.chat(
                model=config.LLM_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
            )
            data = json.loads(response['message']['content'])
            summary = data.get('summary', 'parse_failed')
            tags = data.get('tags', '')
            logger.info(
                'llm_summary_done',
                tags=tags,
                summary_preview=summary[:200],
                prompt_preview=prompt[:200],
            )
            return summary, tags, {'prompt': prompt, 'response': data}
        except Exception as exc:
            logger.error('llm_summary_error', error=str(exc))
            return 'summary_failed', 'error', {'prompt': prompt, 'error': str(exc)}

    def label_emotions(self, segments: list[dict]) -> tuple[list[dict], dict]:
        """Ask LLM to classify emotions per sentence; fallback to neutral."""
        if not segments:
            return segments, {'prompt': None, 'response': None}

        lines = [
            f"{idx}: {seg.get('text', '')}" for idx,
            seg in enumerate(segments)
        ]
        prompt = f"""
Classify the primary emotion for each line below. Use one of:
joy, sadness, anger, fear, surprise, neutral.
Return JSON list with objects: {{"index": <int>, "emotion": "<label>"}}.
Lines:
{chr(10).join(lines)}
""".strip()

        try:
            client = ollama.Client(host=config.OLLAMA_HOST)
            response = client.chat(
                model=config.LLM_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
            )
            data = json.loads(response['message']['content'])
            emotion_map = {
                item.get('index'): item.get(
                    'emotion', 'neutral',
                ) for item in data if isinstance(item, dict)
            }
            for idx, seg in enumerate(segments):
                seg['emotion'] = emotion_map.get(idx, 'neutral')
            logger.info(
                'llm_emotion_done',
                labeled=len(emotion_map),
                prompt_preview=prompt[:200],
            )
            return segments, {'prompt': prompt, 'response': data}
        except Exception as exc:
            logger.warning('llm_emotion_failed', error=str(exc))
            for seg in segments:
                seg.setdefault('emotion', 'neutral')
            return segments, {'prompt': prompt, 'error': str(exc)}
