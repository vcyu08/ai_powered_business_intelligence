# Build Instructions — InsightForge

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | Check: `python --version` |
| pip | ≥ 23.0 | Check: `pip --version` |
| ANTHROPIC_API_KEY | — | Required at runtime; not needed for install |

**System requirements**: Any OS supporting Python 3.11+. Minimum 2 GB RAM (LLM streaming). Internet connection required for Anthropic API calls at runtime.

---

## Build Steps

### 1. Copy Environment File

```bash
cp .env.example .env
```

Open `.env` and replace `your-anthropic-api-key-here` with your real Anthropic API key.

### 2. (Recommended) Create a Virtual Environment

```bash
python -m venv .venv

# Activate — Windows CMD:
.venv\Scripts\activate.bat

# Activate — Windows PowerShell:
.venv\Scripts\Activate.ps1

# Activate — macOS/Linux:
source .venv/bin/activate
```

### 3. Install Production Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Development/Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### 5. Verify Installation

```bash
python -c "import streamlit, langchain_core, langchain_anthropic, anthropic, pandas, plotly, dotenv; print('All dependencies installed successfully')"
```

**Expected output**:
```
All dependencies installed successfully
```

### 6. Run Dependency Security Audit (SECURITY-09)

```bash
pip audit
```

**Expected output**: `No known vulnerabilities found` (or a list of vulnerabilities to address before release).

If vulnerabilities are found: upgrade the affected package to a patched version, update `requirements.txt` with the new pinned version, and re-run `pip audit`.

---

## Build Artifacts

InsightForge is a pure Python application — there are no compiled artifacts. The "build" consists of installed packages in the virtual environment.

| Artifact | Location | Purpose |
|---|---|---|
| Installed packages | `.venv/Lib/site-packages/` | All runtime dependencies |
| Environment config | `.env` | API key (never commit this file) |

---

## Troubleshooting

### `pip install` fails with dependency conflicts
```
ERROR: pip's dependency resolver does not currently take into account all the packages...
```
**Cause**: Version conflicts between pinned packages.
**Solution**: Create a fresh virtual environment, then re-run `pip install -r requirements.txt`. If the conflict persists, update the conflicting package version in `requirements.txt` and re-pin with `pip freeze`.

### `ModuleNotFoundError` when running the app
**Cause**: Running `streamlit run app.py` outside the virtual environment.
**Solution**: Activate the virtual environment first (Step 2), then run the app.

### `pip audit` not found
**Cause**: `pip-audit` is a separate package, not bundled with pip.
**Solution**: `pip install pip-audit`, then re-run `pip audit`.

### PowerShell script execution policy blocks `.venv\Scripts\Activate.ps1`
**Cause**: Windows execution policy restricts unsigned scripts.
**Solution**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then retry activation.
