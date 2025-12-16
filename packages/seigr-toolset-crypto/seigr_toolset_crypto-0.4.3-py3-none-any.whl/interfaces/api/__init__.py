"""
API Interface Module
"""

from .stc_api import (
    STCContext,
    initialize,
    encrypt,
    decrypt,
    hash_data,
    quick_encrypt,
    quick_decrypt
)

__all__ = [
    "STCContext",
    "initialize",
    "encrypt",
    "decrypt",
    "hash_data",
    "quick_encrypt",
    "quick_decrypt"
]
