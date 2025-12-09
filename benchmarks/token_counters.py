"""
Token counting utilities for TOONSTREAM benchmarks.

Supports multiple tokenizers:
1. tiktoken (OpenAI - GPT-4, GPT-3.5)
2. transformers (Hugging Face - Llama, Mistral, etc.)
3. sentencepiece (Google - T5, etc.)
4. Character approximation (fallback)

Usage:
    from token_counters import get_tokenizer, count_tokens

    tokenizer = get_tokenizer('llama')  # or 'gpt4', 'mistral', 'auto'
    tokens = count_tokens("Hello world", tokenizer)
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class TokenizerInfo:
    name: str
    model: str
    tokenizer: Any
    count_fn: Callable[[str], int]
    is_open_source: bool


def _try_tiktoken(model: str = "cl100k_base") -> Optional[TokenizerInfo]:
    """Try to load tiktoken tokenizer."""
    try:
        import tiktoken

        enc = tiktoken.get_encoding(model)
        return TokenizerInfo(
            name="tiktoken",
            model=model,
            tokenizer=enc,
            count_fn=lambda text: len(enc.encode(text)),
            is_open_source=False,  # OpenAI proprietary
        )
    except ImportError:
        return None


def _try_transformers_llama() -> Optional[TokenizerInfo]:
    """Try to load Llama tokenizer via transformers."""
    try:
        from transformers import AutoTokenizer

        # Use Llama-2 tokenizer (open source, same as Llama 3)
        tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Llama-2-7b-hf", use_fast=True, trust_remote_code=True
        )
        return TokenizerInfo(
            name="transformers",
            model="Llama-2",
            tokenizer=tokenizer,
            count_fn=lambda text: len(tokenizer.encode(text)),
            is_open_source=True,
        )
    except Exception:
        return None


def _try_transformers_mistral() -> Optional[TokenizerInfo]:
    """Try to load Mistral tokenizer via transformers."""
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1", use_fast=True)
        return TokenizerInfo(
            name="transformers",
            model="Mistral-7B",
            tokenizer=tokenizer,
            count_fn=lambda text: len(tokenizer.encode(text)),
            is_open_source=True,
        )
    except Exception:
        return None


def _try_transformers_gpt2() -> Optional[TokenizerInfo]:
    """Try to load GPT-2 tokenizer (lightweight, open source)."""
    try:
        from transformers import GPT2Tokenizer

        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        return TokenizerInfo(
            name="transformers",
            model="GPT-2",
            tokenizer=tokenizer,
            count_fn=lambda text: len(tokenizer.encode(text)),
            is_open_source=True,
        )
    except Exception:
        return None


def _try_sentencepiece(model_path: Optional[str] = None) -> Optional[TokenizerInfo]:
    """Try to load SentencePiece tokenizer."""
    try:
        import sentencepiece as spm

        sp = spm.SentencePieceProcessor()
        if model_path:
            sp.Load(model_path)
            return TokenizerInfo(
                name="sentencepiece",
                model=model_path,
                tokenizer=sp,
                count_fn=lambda text: len(sp.EncodeAsIds(text)),
                is_open_source=True,
            )
        return None
    except Exception:
        return None


def _char_approximation() -> TokenizerInfo:
    """Fallback: approximate tokens from character count."""
    return TokenizerInfo(
        name="char_approx",
        model="~4 chars/token",
        tokenizer=None,
        count_fn=lambda text: max(1, len(text) // 4),
        is_open_source=True,
    )


def get_tokenizer(model: str = "auto") -> TokenizerInfo:
    """
    Get a tokenizer by name or auto-detect best available.

    Args:
        model: One of 'auto', 'gpt4', 'llama', 'mistral', 'gpt2', 'char'

    Returns:
        TokenizerInfo with name, model, and count function
    """
    if model == "auto":
        # Try open source first (user preference), then fall back
        attempts = [
            ("gpt2", _try_transformers_gpt2),
            ("llama", _try_transformers_llama),
            ("mistral", _try_transformers_mistral),
            ("tiktoken", lambda: _try_tiktoken()),
        ]
        for name, fn in attempts:
            result = fn()
            if result:
                return result
        return _char_approximation()

    elif model in ("gpt4", "tiktoken", "openai"):
        result = _try_tiktoken("cl100k_base")
        if result:
            return result
        raise ImportError("tiktoken not installed: pip install tiktoken")

    elif model == "llama":
        result = _try_transformers_llama()
        if result:
            return result
        raise ImportError("transformers not installed or Llama model not accessible")

    elif model == "mistral":
        result = _try_transformers_mistral()
        if result:
            return result
        raise ImportError("transformers not installed or Mistral model not accessible")

    elif model == "gpt2":
        result = _try_transformers_gpt2()
        if result:
            return result
        raise ImportError("transformers not installed: pip install transformers")

    elif model == "char":
        return _char_approximation()

    else:
        raise ValueError(f"Unknown tokenizer: {model}. Use: auto, gpt4, llama, mistral, gpt2, char")


def count_tokens(text: str, tokenizer: Optional[TokenizerInfo] = None) -> int:
    """
    Count tokens in text using specified tokenizer.

    Args:
        text: The text to tokenize
        tokenizer: TokenizerInfo from get_tokenizer(), or None for auto

    Returns:
        Number of tokens
    """
    if tokenizer is None:
        tokenizer = get_tokenizer("auto")
    return tokenizer.count_fn(text)


def list_available_tokenizers() -> dict:
    """
    List all available tokenizers on this system.

    Returns:
        Dict mapping tokenizer name to availability status
    """
    available = {}

    # Check tiktoken
    try:
        import tiktoken

        available["tiktoken (GPT-4/3.5)"] = True
    except ImportError:
        available["tiktoken (GPT-4/3.5)"] = False

    # Check transformers
    try:
        import transformers

        available["transformers"] = True

        # Check specific models
        try:
            from transformers import GPT2Tokenizer

            GPT2Tokenizer.from_pretrained("gpt2")
            available["GPT-2 (open source)"] = True
        except Exception:
            available["GPT-2 (open source)"] = False

    except ImportError:
        available["transformers"] = False
        available["GPT-2 (open source)"] = False

    # Check sentencepiece
    try:
        import sentencepiece

        available["sentencepiece"] = True
    except ImportError:
        available["sentencepiece"] = False

    # Character approximation always available
    available["char_approx (fallback)"] = True

    return available


if __name__ == "__main__":
    print("=" * 60)
    print("TOONSTREAM Token Counter - Available Tokenizers")
    print("=" * 60)

    available = list_available_tokenizers()
    for name, status in available.items():
        icon = "✓" if status else "✗"
        print(f"  {icon} {name}")

    print("\n" + "-" * 60)
    print("Testing auto-detected tokenizer:")
    print("-" * 60)

    tokenizer = get_tokenizer("auto")
    print(f"\n  Tokenizer: {tokenizer.name}")
    print(f"  Model: {tokenizer.model}")
    print(f"  Open Source: {tokenizer.is_open_source}")

    # Test with sample text
    test_texts = [
        'name="Alice";age=30',
        '{"name":"Alice","age":30}',
        "user.profile.name=Alice;user.profile.age=30",
    ]

    print("\n  Sample token counts:")
    for text in test_texts:
        tokens = count_tokens(text, tokenizer)
        print(f"    {tokens:3d} tokens: {text}")

    print("\n" + "=" * 60)
