#!/usr/bin/env python3
"""Reducer compatible con Hadoop Streaming: suma valores por clave (entrada ordenada por clave)."""
import sys
actual, total = None, 0
for line in sys.stdin:
    k, v = line.rstrip("\n").split("\t")
    if k != actual:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual, total = k, 0
    total += int(v)
if actual is not None:
    print(f"{actual}\t{total}")
