"""
Utilities for extracting parameters from natural language input.

This module provides tools for parsing user input and extracting
structured parameters that abilities need.
"""

import re
from datetime import datetime, timedelta
from re import Pattern

import structlog
from dateutil import parser as date_parser

logger = structlog.get_logger(__name__)


class ParameterExtractor:
    """
    Utility class for extracting parameters from natural language.

    Provides methods for parsing common parameter types like numbers,
    dates, durations, and named entities from user input.
    """

    # Common regex patterns
    DURATION_PATTERN: Pattern = re.compile(
        r"(?:(\d+)\s*(?:hours?|hrs?|h))?"
        r"\s*(?:(\d+)\s*(?:minutes?|mins?|m))?"
        r"\s*(?:(\d+)\s*(?:seconds?|secs?|s))?",
        re.IGNORECASE,
    )

    NUMBER_PATTERN: Pattern = re.compile(r"[-+]?\d*\.?\d+")

    @staticmethod
    def extract_duration(text: str) -> timedelta | None:
        """
        Extract a duration from natural language text.

        Args:
            text: Input text containing duration

        Returns:
            timedelta object or None if no duration found

        Examples:
            "2 hours" -> timedelta(hours=2)
            "30 minutes" -> timedelta(minutes=30)
            "1 hour 30 minutes" -> timedelta(hours=1, minutes=30)
        """
        match = ParameterExtractor.DURATION_PATTERN.search(text)
        if not match:
            return None

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        if hours == 0 and minutes == 0 and seconds == 0:
            return None

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def extract_datetime(text: str, base_time: datetime | None = None) -> datetime | None:
        """
        Extract a datetime from natural language text.

        Args:
            text: Input text containing date/time
            base_time: Reference time for relative dates (defaults to now)

        Returns:
            datetime object or None if no date found

        Examples:
            "tomorrow at 3pm" -> datetime(...)
            "in 2 hours" -> datetime(...)
            "next Monday" -> datetime(...)
        """
        if base_time is None:
            base_time = datetime.now()

        try:
            # Try parsing with dateutil
            parsed = date_parser.parse(text, default=base_time, fuzzy=True)
            return parsed
        except (ValueError, OverflowError):
            logger.debug("Failed to parse datetime", text=text)
            return None

    @staticmethod
    def extract_number(text: str) -> float | None:
        """
        Extract a number from text.

        Args:
            text: Input text containing number

        Returns:
            Float value or None if no number found

        Examples:
            "set timer for 5 minutes" -> 5.0
            "temperature is 72.5 degrees" -> 72.5
        """
        match = ParameterExtractor.NUMBER_PATTERN.search(text)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
        return None

    @staticmethod
    def extract_numbers(text: str) -> list[float]:
        """
        Extract all numbers from text.

        Args:
            text: Input text

        Returns:
            List of float values
        """
        matches = ParameterExtractor.NUMBER_PATTERN.findall(text)
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        return numbers

    @staticmethod
    def extract_quoted_text(text: str) -> list[str]:
        """
        Extract text within quotes.

        Args:
            text: Input text

        Returns:
            List of quoted strings

        Examples:
            'remind me to "buy milk"' -> ["buy milk"]
            "set title 'Meeting Notes'" -> ["Meeting Notes"]
        """
        # Match both single and double quotes
        pattern = r'"([^"]*)"|\'([^\']*)\''
        matches = re.findall(pattern, text)
        # Flatten the tuples and filter empty strings
        return [match for group in matches for match in group if match]

    @staticmethod
    def extract_tags(text: str) -> list[str]:
        """
        Extract hashtags from text.

        Args:
            text: Input text

        Returns:
            List of tags (without # symbol)

        Examples:
            "note about #project #work" -> ["project", "work"]
        """
        pattern = r"#(\w+)"
        return re.findall(pattern, text)

    @staticmethod
    def extract_priority(text: str) -> str | None:
        """
        Extract priority level from text.

        Args:
            text: Input text

        Returns:
            Priority level ("high", "medium", "low") or None

        Examples:
            "high priority task" -> "high"
            "low priority reminder" -> "low"
        """
        text_lower = text.lower()

        if re.search(r"\b(high|urgent|important|critical)\b", text_lower):
            return "high"
        elif re.search(r"\blow\b", text_lower):
            return "low"
        elif re.search(r"\bmedium\b", text_lower):
            return "medium"

        return None

    @staticmethod
    def extract_boolean(text: str, keywords: dict[str, bool]) -> bool | None:
        """
        Extract boolean value based on keywords.

        Args:
            text: Input text
            keywords: Dictionary mapping keywords to boolean values

        Returns:
            Boolean value or None

        Examples:
            extract_boolean("enable notifications", {"enable": True, "disable": False})
            -> True
        """
        text_lower = text.lower()

        for keyword, value in keywords.items():
            if keyword.lower() in text_lower:
                return value

        return None

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Trim
        text = text.strip()

        return text

    @staticmethod
    def extract_name_value_pairs(text: str) -> dict[str, str]:
        """
        Extract name-value pairs from text.

        Args:
            text: Input text with name:value or name=value patterns

        Returns:
            Dictionary of name-value pairs

        Examples:
            "title: Meeting Notes, category: Work"
            -> {"title": "Meeting Notes", "category": "Work"}
        """
        pairs = {}

        # Match patterns like "name: value" or "name = value"
        pattern = r"(\w+)\s*[:=]\s*([^,]+)"
        matches = re.findall(pattern, text)

        for name, value in matches:
            pairs[name.strip()] = value.strip()

        return pairs
