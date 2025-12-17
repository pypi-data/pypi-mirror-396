## recallia

Minimal voice-to-notes pipeline with FunASR + Ollama.

### Quickstart (Docker)
1) Requirements: Docker & docker-compose; NVIDIA GPU + container toolkit recommended; Ollama (runs as a service in compose).
2) (Optional) Reuse host Ollama models: set `HOST_OLLAMA_MODELS=/path/to/host/.ollama` before `docker compose up`.
3) Build & run:
   ```bash
   docker compose up --build
   ```
4) Drop audio files (`.mp3/.wav/.m4a/.aac`) into `data/inbox/`. Outputs land in `data/archive/YYYY-MM-DD/<hash>/`.

### Flow
- ASR via FunASR (GPU if available).
- Summaries/tags + per-sentence emotions via Ollama.
- Artifacts per file: original audio, `transcript.jsonl`, `llm_summary.json`, `llm_emotion.json`, `run.log`.
- Metadata in SQLite `data/db.sqlite3`.

### Config
- `docker-compose.yaml`: `OLLAMA_HOST` (defaults to `http://ollama:11434`), GPU flags, caches (`./cache`, `./modelscope`, optional `HOST_OLLAMA_MODELS`).
- `recallia/config.py`: ASR device, LLM model, base paths.

### Local (no Docker)
```bash
uv sync
python -m recallia
```
Ensure Ollama reachable at `OLLAMA_HOST`.

### Demo data
Use `examples/generate_demo_data.py` to produce sample audio/text for testing.

### Example archive (real output)
`data/archive/2025-12-15/7daf3d771c04/`
```
- 02_emergency_call.mp3
- transcript.jsonl
- llm_summary.json
- llm_emotion.json
- run.log
```
- `run.log` key fields:
  - summary: 技术人员发现API网关出现502错误，原因是数据库连接延迟导致CPU负载过高和慢查询问题。决定手动添加索引并切换流量以缓解当前状况。
  - tags: api网关, 数据库连接, 索引
  - duration_sec: 7.064
- `llm_summary.json` snippet:
```json
{
  "response": {
    "summary": "技术人员发现API网关出现502错误，原因是数据库连接延迟导致CPU负载过高和慢查询问题。决定手动添加索引并切换流量以缓解当前状况。",
    "tags": "api网关, 数据库连接, 索引"
  }
}
```
- `transcript.jsonl` starts with full text, then per-segment entries. Excerpt:
```json
{"type": "full_text", "text": "Speaker 0: 喂，老张听得到吗？出大问题了， api 网关全是五百零二报错。\nSpeaker 2: 听到了，我刚看监控，数据库连接迟爆了， cpu 直接飙到百分之一百，\n..."}
{"type": "segment", "speaker": "Speaker 0", "text": "喂，", "start_time": 290, "end_time": 530, "emotion": "neutral"}
{"type": "segment", "speaker": "Speaker 2", "text": "数据库连接迟爆了，", "start_time": 10860, "end_time": 12400, "emotion": "neutral"}
```
