# llmtrace-lite

Zero-config decorator for tracing LLM calls. Print-debugging for language model functions, nothing more.

## What this is

A tiny Python decorator that logs basic metadata about LLM function calls: timing, model name, prompt/output sizes, and success/failure status. No dependencies, no configuration files, no dashboards. Just readable logs.

## Installation

```bash
pip install llmtrace-lite
```

## Usage

```python
from llmtrace_lite import trace

@trace
def call_llm(prompt, model="gpt-4o"):
    # Your LLM call here
    response = some_llm_client.complete(prompt, model=model)
    return response

# Use it normally
result = call_llm("Explain quantum computing", model="gpt-4o")
```

**Output:**

```text
[llmtrace] call_llm
  model: gpt-4o
  latency_ms: 842
  prompt_chars: 312
  output_chars: 1187
  status: success
```

## File logging

Set `LLMTRACE_FILE` to append JSON lines instead:

```bash
export LLMTRACE_FILE=traces.jsonl
python your_script.py
```

Each line is a JSON object with trace metadata.

## What this captures

- Function name
- Start/end timestamps
- Latency (milliseconds)
- Status (`success` or `error`)
- Exception details (if error)
- Model name (if passed as `model` kwarg)
- Prompt size (characters, if arg named `prompt`)
- Output size (characters, if return is string)
- Retry count (if function has `retries` attribute)

## What this is NOT

This is not:
- An observability platform
- A provider-specific SDK integration
- An async framework
- A monitoring dashboard
- A production tracing system
- Extensible middleware

If you need those things, use LangSmith, Phoenix, or OpenTelemetry.

This is for local debugging and quick sanity checks. That's it.

## Requirements

- Python 3.9+
- Standard library only
- No external dependencies

## License

MIT