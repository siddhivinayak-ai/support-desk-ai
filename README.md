# support-desk-ai

The AI helpers behind a customer-support desk, written in early 2024:

- **Ticket summaries** for the agent sidebar (`desk/summarize.py`)
- **Urgency triage** on every incoming ticket (`desk/triage.py`)
- **Voicemail transcription** (`desk/voice.py`)
- **Help-center illustrations** for new articles (`desk/visuals.py`)
- **Similar-ticket search** over embeddings, plus a moderation check before auto-replies (`desk/search.py`)

It uses the OpenAI Python SDK (`openai==1.40.0`) and pins specific model snapshots, so behaviour
doesn't drift when an alias moves. It runs on Python 3.11 (`runtime.txt`, `.python-version`).

## Run it

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                             # add OPENAI_API_KEY
python app.py                                    # http://localhost:5001

# tests (OpenAI is mocked; no key or network needed)
pip install -r requirements-dev.txt
python -m pytest -q                              # 4 passed
```

## OpenAI calls in this code

| Where | Call | Model |
|---|---|---|
| `desk/summarize.py:20` | `client.chat.completions.create` | `SUMMARY_MODEL = "gpt-4-0613"` (a constant on line 11) |
| `desk/triage.py:13` | `client.chat.completions.create` | `"gpt-3.5-turbo-0125"` |
| `desk/voice.py:10` | `client.audio.transcriptions.create` | `"whisper-1"` |
| `desk/visuals.py:9` | `client.images.generate` | `"gpt-image-1"` |
| `desk/search.py:11` | `client.embeddings.create` | `EMBEDDING_MODEL = "text-embedding-3-small"` (line 7) |
| `desk/search.py:16` | `client.moderations.create` | `"omni-moderation-latest"` |

---

## Testing with Self-Maintaining APIs: what to expect

Everything here comes from **real vendor data**: OpenAI's own deprecations page, which SMA monitors.
There's no demo fixture, and `DEMO_FIXTURES_ENABLED` stays `false`. The results below were
measured by running SMA's real pipeline on this exact code: scan, impact, then a fix for each
model, with tests in the Docker sandbox. Only the pull requests weren't opened.

### 1. Scan

- **6 OpenAI calls** found, all matched to the catalog (0 unknown): chat completions ×2,
  transcription, image generation, embeddings, moderation. 12 references in total, including
  the imports and the `OPENAI_API_KEY` name.
- If `.env.example` / `.python-version` are missing on GitHub (web upload skips dotfiles), the
  reference count is lower. Nothing else changes: `runtime.txt` still pins Python 3.11.

### 2. Changes and impact (automatic after the scan)

SMA checks the scanned code against all 48 shutdowns OpenAI has announced. Exactly 4 hit this code:

| Call site | Impact | Why |
|---|---|---|
| `desk/summarize.py:20` | **Critical / affected** | passes `gpt-4-0613` (through `SUMMARY_MODEL`), shut down **2026-10-23** |
| `desk/triage.py:13` | **Critical / affected** | passes `gpt-3.5-turbo-0125`, shut down **2026-10-23** |
| `desk/visuals.py:9` | **Critical / affected** | passes `gpt-image-1`, shut down **2026-10-23** |
| `desk/voice.py:10` | **Critical / affected** | passes `whisper-1`, shut down **2027-02-26** |

The other 44 deprecations show **not affected**: every call passes a model, and none passes
those. `text-embedding-3-small` and `omni-moderation-latest` aren't being retired.

### 3. Prepare fix (one per change)

| Change | Result |
|---|---|
| `gpt-4-0613` | Edits the **constant**: `SUMMARY_MODEL = "gpt-5.6-sol"` (1 line in `desk/summarize.py`) |
| `gpt-3.5-turbo-0125` | `model="gpt-5.6-terra"` in `desk/triage.py` |
| `gpt-image-1` | `model="gpt-image-2"` in `desk/visuals.py` |
| `whisper-1` | **Needs manual review**: OpenAI recommends "gpt-live-transcribe *or* gpt-transcribe", a choice SMA won't make for you |

For each automatic fix, validation runs in Docker (`python:3.11-slim`, no network during tests):
source safety ✓, syntax ✓, dependencies installed (about 1.5–2.5 min the first time), tests
**before the patch: 4 passed**, static checks skipped (no linter configured), tests **after the
patch: 4 passed**. The fix then waits for your approval.

### 4. Approve & open PR

You get a branch `sma/openai/deprecated/<id8>` and a pull request that changes one line in one
file. The body covers why (OpenAI's shutdown date and source), the validation table, the impact
sentence and a review checklist. Nothing is merged, and `main` isn't touched. Approving again
returns the same PR.
