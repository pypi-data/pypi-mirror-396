"""Enum representing LLM model types."""

from enum import Enum


class ModelTypes(str, Enum):
    """Enum representing different LLM model types."""

    # Azure
    GPT_41 = "gpt-4.1"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_4o_2024_08_06 = "gpt-4o-2024-08-06"
    GPT_4o_2024_11_20 = "gpt-4o-2024-11-20"
    GPT_4o_MINI = "gpt-4o-mini"
    O3_MINI = "o3-mini"
    O3_2025_04_16 = "o3-2025-04-16"
    O4_MINI_2025_04_16 = "o4-mini-2025-04-16"
    O1 = "o1"
    GPT_5_2025_08_07 = "gpt-5-2025-08-07"
    GPT_5_NANO_2025_08_07 = "gpt-5-nano-2025-08-07"
    GPT_5_MINI_2025_08_07 = "gpt-5-mini-2025-08-07"

    # GCP
    CLAUDE_SONNET_V2_VERTEX = "claude-sonnet-v2-vertex"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_20_FLASH = "gemini-2.0-flash"
    GEMINI_25_FLASH = "gemini-2.5-flash"
    GEMINI_25_PRO = "gemini-2.5-pro"
    CLAUDE_SONNET_37_VERTEX = "claude-sonnet-3-7-vertex"
    GEMINI_3_PRO = "gemini-3-pro"

    # Bedrock
    CLAUDE_35_SONNET = "claude-3-5-sonnet"
    CLAUDE_35_SONNET_V2 = "claude-3-5-sonnet-v2"
    CLAUDE_37_SONNET_V1 = "claude-3-7"
    CLAUDE_4_SONNET = "claude-4-sonnet"
    CLAUDE_4_5_SONNET = "claude-4-5-sonnet"
    CLAUDE_4_OPUS = "claude-4-opus"
    CLAUDE_4_1_OPUS = "claude-4-1-opus"
    CLAUDE_4_5_OPUS = "claude-opus-4-5-20251101"
    CLAUDE_4_SONNET_1M = "claude-4-sonnet-1m"
    CLAUDE_4_5_HAIKU = "claude-haiku-4-5-20251001"

    # Other
    DEEPSEEK_R1 = "deepseek-r1"
