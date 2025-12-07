"""
Multilingual Prompts Module

Control the language via the MEMORY_LANGUAGE environment variable, supports 'en' and 'zh'.
Default is English ('en').

Usage:
1. Set environment variable: export MEMORY_LANGUAGE=zh
2. No code changes needed, import directly from memory_layer.prompts

Example:
    from memory_layer.prompts import (
        EPISODE_GENERATION_PROMPT,
        CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT,
        get_foresight_generation_prompt,
    )
"""

import os

# Get language setting, default to English
MEMORY_LANGUAGE = os.getenv('MEMORY_LANGUAGE', 'en').lower()

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'zh']

if MEMORY_LANGUAGE not in SUPPORTED_LANGUAGES:
    print(f"Warning: Unsupported language '{MEMORY_LANGUAGE}', falling back to 'en'")
    MEMORY_LANGUAGE = 'en'

# Dynamically import prompts based on language setting
if MEMORY_LANGUAGE == 'zh':
    # ===== Chinese Prompts =====
    # Conversation related
    from .zh.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT, CONV_SUMMARY_PROMPT

    # Episode related
    from .zh.episode_mem_prompts import (
        EPISODE_GENERATION_PROMPT,
        GROUP_EPISODE_GENERATION_PROMPT,
        DEFAULT_CUSTOM_INSTRUCTIONS,
    )

    # Profile related
    from .zh.profile_mem_prompts import CONVERSATION_PROFILE_EXTRACTION_PROMPT
    from .zh.profile_mem_part1_prompts import (
        CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT,
    )
    from .zh.profile_mem_part2_prompts import (
        CONVERSATION_PROFILE_PART2_EXTRACTION_PROMPT,
    )
    from .zh.profile_mem_part3_prompts import (
        CONVERSATION_PROFILE_PART3_EXTRACTION_PROMPT,
    )
    from .zh.profile_mem_evidence_completion_prompt import (
        CONVERSATION_PROFILE_EVIDENCE_COMPLETION_PROMPT,
    )

    # Group Profile related
    from .zh.group_profile_prompts import (
        CONTENT_ANALYSIS_PROMPT,
        BEHAVIOR_ANALYSIS_PROMPT,
    )

    # Foresight related
    from .zh.foresight_prompts import (
        get_group_foresight_generation_prompt,
        get_foresight_generation_prompt,
    )

    # Event Log related
    from .zh.event_log_prompts import EVENT_LOG_PROMPT

else:
    # ===== English Prompts (default) =====
    # Conversation related
    from .en.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT, CONV_SUMMARY_PROMPT

    # Episode related
    from .en.episode_mem_prompts import (
        EPISODE_GENERATION_PROMPT,
        GROUP_EPISODE_GENERATION_PROMPT,
        DEFAULT_CUSTOM_INSTRUCTIONS,
    )

    # Profile related
    from .en.profile_mem_prompts import CONVERSATION_PROFILE_EXTRACTION_PROMPT
    from .en.profile_mem_part1_prompts import (
        CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT,
    )
    from .en.profile_mem_part2_prompts import (
        CONVERSATION_PROFILE_PART2_EXTRACTION_PROMPT,
    )
    from .en.profile_mem_part3_prompts import (
        CONVERSATION_PROFILE_PART3_EXTRACTION_PROMPT,
    )
    from .en.profile_mem_evidence_completion_prompt import (
        CONVERSATION_PROFILE_EVIDENCE_COMPLETION_PROMPT,
    )

    # Group Profile related
    from .en.group_profile_prompts import (
        CONTENT_ANALYSIS_PROMPT,
        BEHAVIOR_ANALYSIS_PROMPT,
    )

    # Foresight related
    from .en.foresight_prompts import (
        get_group_foresight_generation_prompt,
        get_foresight_generation_prompt,
    )

    # Event Log related
    from .en.event_log_prompts import EVENT_LOG_PROMPT

# Export current language info
CURRENT_LANGUAGE = MEMORY_LANGUAGE
