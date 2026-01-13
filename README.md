# llama-stack aiosqlite Hang Reproducer

Minimal reproducer for a process hang when using `LlamaStackAsLibraryClient` with aiosqlite 0.22+.

## Problem

When using `LlamaStackAsLibraryClient`, the process hangs indefinitely on exit. This is caused by aiosqlite's worker thread not being properly terminated.

### Root Cause

In aiosqlite 0.22.0, the `_connection_worker_thread` was changed from a daemon thread to a non-daemon thread:
- **aiosqlite < 0.22**: Worker thread is daemon, so Python exits immediately
- **aiosqlite >= 0.22**: Worker thread is non-daemon, so Python's `threading._shutdown()` waits for it to terminate

The worker thread runs in an infinite loop waiting on a queue:
```python
def _connection_worker_thread(tx: _TxQueue):
    while True:
        future, function = tx.get()  # Blocks forever
        result = function()
        if result is _STOP_RUNNING_SENTINEL:
            break
```

The only way to exit the loop is when `_STOP_RUNNING_SENTINEL` is sent via `Connection.close()`. If llama-stack doesn't properly close its aiosqlite connections, the thread blocks forever.

## Reproducing

```bash
# Reproduces hang (aiosqlite >= 0.22):
uv run reproducer.py

# Works correctly (aiosqlite == 0.21.0):
uv run --with 'aiosqlite==0.21.0' reproducer.py
```

## Workarounds

1. **Pin aiosqlite==0.21.0** (recommended until llama-stack fixes the issue)
2. **Call `os._exit(0)` at the end of main()** (bypasses thread cleanup, may lose buffered output)

## Related

- aiosqlite changelog: https://aiosqlite.omnilib.dev/en/stable/changelog.html (v0.22.0 changes)
