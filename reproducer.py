#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "llama-stack[client]",
#     "aiosqlite>=0.22",
#     "sentence-transformers",
#     "faiss-cpu",
# ]
# ///
"""
Minimal reproducer for llama-stack aiosqlite hang.

With aiosqlite >= 0.22, this script hangs after printing "Work complete".
With aiosqlite == 0.21.0, it exits cleanly.

The hang is caused by LlamaStackAsLibraryClient not properly closing
aiosqlite connections, leaving the worker thread blocking on queue.get().

Usage:
    # Reproduces hang (aiosqlite >= 0.22):
    uv run reproducer.py

    # Works correctly (aiosqlite == 0.21.0):
    uv run --with 'aiosqlite==0.21.0' reproducer.py
"""


def main():
    print("Importing llama_stack...", flush=True)
    from llama_stack.core.library_client import LlamaStackAsLibraryClient

    print("Creating LlamaStackAsLibraryClient...", flush=True)
    client = LlamaStackAsLibraryClient(
        "./run.yaml",
        provider_data={},
    )

    print("Initializing client...", flush=True)
    client.initialize()

    print("Listing providers...", flush=True)
    providers = client.providers.list()
    print(f"Found {len(providers)} providers", flush=True)

    print("Closing client...", flush=True)
    client.close()

    print("Work complete, exiting...", flush=True)
    # With aiosqlite >= 0.22, process hangs here
    # The aiosqlite worker thread is non-daemon and blocks on queue.get()


if __name__ == "__main__":
    main()
    print("main() returned, script ending", flush=True)

    # Uncomment to force exit (workaround):
    # import os
    # import sys
    # sys.stdout.flush()
    # sys.stderr.flush()
    # os._exit(0)
