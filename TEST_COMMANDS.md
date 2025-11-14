# Quick Test Commands

## Run Comprehensive Test Suite

```bash
cd /Users/nithinyanna/Downloads/omnisync
cd examples
source ../sdk/python/venv/bin/activate
python3 test_improvements.py
```

## Or from project root:

```bash
cd /Users/nithinyanna/Downloads/omnisync
python3 examples/test_improvements.py
```

## What the test covers:

✅ **A. Session + Trace ID Propagation**
   - Verifies IDs are generated at start
   - Checks propagation through messages
   - Ensures no "None" values

✅ **B. Ollama Session Handling**
   - Tests proper session cleanup
   - Verifies no "Unclosed client session" warnings
   - Handles Ollama unavailability gracefully

✅ **C. ACK Intent**
   - Creates ACK messages
   - Validates content structure
   - Tests protocol-level acknowledgments

✅ **D. Metadata Enrichment**
   - Checks cpu_usage, mem_usage
   - Verifies response_time_ms
   - Tests framework_version

✅ **E. Schema v0.2 Validation**
   - Validates messages against osp-0.2.json
   - Checks schema_version field
   - Ensures all new fields are valid

✅ **F. Trace Visualization**
   - Generates Mermaid sequence diagrams
   - Prepares D3 force graph data
   - Creates trace logs (text, JSON, CSV)
   - Generates trace summaries

## Expected Output:

You should see:
- ✅ for each passing test
- ❌ for any failures
- Summary at the end showing X/6 tests passed

## Requirements:

- Backend running (for session/trace test)
- psutil installed (for metadata enrichment)
- jsonschema installed (for validation)
