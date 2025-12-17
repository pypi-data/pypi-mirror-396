"""
License sub-module of the Jacobi Library.
"""
from __future__ import annotations
import collections.abc
__all__: list[str] = ['activate', 'activate_cli', 'verify']
def activate(arg0: collections.abc.Sequence[str]) -> int:
    ...
def activate_cli() -> int:
    ...
def verify() -> dict:
    ...
