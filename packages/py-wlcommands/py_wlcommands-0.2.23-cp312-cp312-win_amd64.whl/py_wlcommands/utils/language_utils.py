"""
Language detection utilities for WL Commands.
"""

import locale
import os


def _is_system_chinese() -> bool:
    """
    Check if the system language is Chinese.

    Returns:
        bool: True if system language is Chinese, False otherwise
    """
    try:
        # Try different locale-related environment variables
        lang = (
            os.environ.get("LANG", "")
            or os.environ.get("LANGUAGE", "")
            or os.environ.get("LC_ALL", "")
            or os.environ.get("LC_MESSAGES", "")
        )

        # Fall back to locale.getlocale() if environment variables don't provide language info
        if not lang:
            try:
                locale_value = locale.getlocale()[0]  # Get language code from locale
                if locale_value:
                    lang = locale_value
            except (ValueError, TypeError):
                # If getlocale() fails, use empty string
                pass

        # Check if any of the locale identifiers contain Chinese language codes
        return any(chinese_lang in lang.lower() for chinese_lang in ["zh", "chinese"])
    except (OSError, KeyError, ValueError):
        # If we can't determine the language, default to English
        return False


def _should_display_language(lang: str) -> bool:
    """
    Check if message in specified language should be displayed.

    Args:
        lang (str): Language of the message ("en" or "zh")

    Returns:
        bool: True if message should be displayed
    """
    try:
        from .config import get_config

        language_setting = get_config("language", "auto")

        # If language is set to auto, display based on system language
        if language_setting == "auto":
            # If system language is Chinese, only show Chinese messages
            # Otherwise, show English messages
            is_system_chinese = _is_system_chinese()
            return (lang == "zh" and is_system_chinese) or (
                lang == "en" and not is_system_chinese
            )

        # If language is set to specific language, only display that language
        return language_setting == lang
    except (ImportError, KeyError):
        # Default to showing English if config is not available
        return lang == "en"
