#! /usr/bin/env python
# -*- coding: utf-8 -*-
# tests/test_checksums.py

from pathlib import Path
from gladiator.checksums import md5_base64_file, sha256_file
import hashlib, base64, os, tempfile


def test_md5_base64_file_matches_python():
    payload = b"hello world"
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(payload)
        p = Path(tf.name)
    try:
        expected = base64.b64encode(hashlib.md5(payload).digest()).decode("ascii")
        assert md5_base64_file(p) == expected
    finally:
        os.unlink(p)


def test_sha256_file_matches_python():

    payload = (
        b"The quick brown fox jumps over the lazy dog" * 1000
    )  # large enough for chunking
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(payload)
        path = Path(tf.name)

    try:
        # Expected hash from Python's hashlib
        expected = hashlib.sha256(payload).hexdigest()
        # Verify our implementation returns identical digest
        assert sha256_file(path) == expected

        # Also verify it works with a very small chunk size (forces multiple reads)
        assert sha256_file(path, chunk_size=8) == expected

        # Empty file case
        empty = Path(tempfile.mkstemp()[1])
        try:
            assert sha256_file(empty) == hashlib.sha256(b"").hexdigest()
        finally:
            os.unlink(empty)

    finally:
        os.unlink(path)
