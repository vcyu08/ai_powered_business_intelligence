# Security Test Instructions — InsightForge

## Applicable Security Rules

| Rule | Requirement | Test |
|---|---|---|
| SECURITY-03 | Structured logging; no sensitive data in logs | Inspect log output |
| SECURITY-05 | Input validation ≤ 1,000 chars | Manual UI test |
| SECURITY-09 | No known CVEs in dependencies | `pip audit` |
| SECURITY-10 | All dependencies pinned with `==` | Inspect requirements.txt |
| SECURITY-12 | API key via .env; never hardcoded | Source inspection |
| SECURITY-15 | Generic error messages to user | Manual error injection |

---

## Test 1: Dependency Vulnerability Scan (SECURITY-09)

```bash
pip install pip-audit
pip audit
```

**Expected**: `No known vulnerabilities found`

**If vulnerabilities found**:
1. Note the CVE ID and affected package
2. Check if a patched version exists: `pip index versions <package>`
3. Update `requirements.txt` with the patched version
4. Re-run `pip audit` until clean

---

## Test 2: Pinned Dependency Verification (SECURITY-10)

```bash
python -c "
lines = open('requirements.txt').readlines()
for line in lines:
    line = line.strip()
    if line and not line.startswith('#'):
        assert '==' in line, f'Not pinned: {line}'
        print(f'OK: {line}')
print('PASS: All production dependencies are pinned with ==')
"
```

**Expected**: Each dependency line shows `OK: package==version`.

---

## Test 3: API Key Not Hardcoded (SECURITY-12)

```bash
python -c "
import os, glob
source_files = glob.glob('*.py')
api_key = os.getenv('ANTHROPIC_API_KEY', '')
for f in source_files:
    content = open(f).read()
    if api_key and api_key in content:
        print(f'FAIL: API key found in {f}')
    elif 'sk-ant-' in content or 'ANTHROPIC_API_KEY' in content.replace('os.getenv', '').replace('.env', ''):
        print(f'WARNING: Possible hardcoded key pattern in {f} — verify manually')
    else:
        print(f'OK: {f}')
"
```

Also verify `.gitignore` excludes `.env`:
```bash
python -c "
content = open('.gitignore').read()
assert '.env' in content, 'FAIL: .env not in .gitignore'
print('PASS: .env is excluded from git')
"
```

---

## Test 4: Input Validation (SECURITY-05)

Start the app (`streamlit run app.py`) and test manually in the browser:

**Test 4a — Empty input**:
- Submit an empty query (press Enter with nothing typed)
- **Expected**: Warning "Please enter a question." — chat history unchanged

**Test 4b — Over-length input**:
- Paste a string of 1,001 characters into the chat input
- **Expected**: Warning "Query too long (1001 chars). Limit: 1,000 characters." — chat history unchanged

**Test 4c — Whitespace-only input**:
- Type several spaces and press Enter
- **Expected**: Warning "Please enter a question." (strips to empty)

---

## Test 5: Error Messages Do Not Expose Internals (SECURITY-15)

**Test 5a — Invalid API key**:
1. Set `ANTHROPIC_API_KEY=invalid-key-123` in `.env`
2. Restart the app and submit a query
3. **Expected**: Chat area shows "An error occurred while processing your request. Please try again." — no stack trace, no API key value, no internal error details visible

**Test 5b — Evaluation failure**:
1. The evaluator uses the same API key. With an invalid key, evaluation also fails.
2. **Expected**: Score displays "⚠️ Evaluation unavailable" — no exception details shown

Restore your real API key in `.env` after this test.

---

## Test 6: Structured Logging — No Sensitive Data (SECURITY-03)

Run the app with debug output captured:

```bash
streamlit run app.py 2>&1 | head -50
```

Inspect the log lines. Verify:
- ✅ No API key value appears in any log line
- ✅ No full user query text appears in WARNING-level logs
- ✅ Only exception type names appear in error logs (e.g., `AuthenticationError`, not full stack traces)
- ✅ Log format includes timestamp and module name

**Expected log format** (WARNING+ only):
```
2026-06-13T12:00:00 data_processor WARNING Loaded 1000 records from sales_data.csv
```

No sensitive content should appear in this output.
