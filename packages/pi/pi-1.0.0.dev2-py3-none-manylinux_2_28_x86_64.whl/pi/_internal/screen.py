"""Module for scanning and replacing sensitive data in text."""

from __future__ import annotations

import collections
import re
import math

from typing import Pattern


# Common patterns for sensitive environment variables and field names
# Based on industry standards from Sentry, Django, detect-secrets, etc.
SENSITIVE_PATTERNS = [
    # Authentication and secrets
    "PASSWORD",
    "PASSWD",
    "PWD",
    "PASS",
    "PASSPHRASE",
    "SECRET",
    "SECRET_KEY",
    "API_KEY",
    "APIKEY",
    "ACCESS_KEY",
    "AUTH_TOKEN",
    "TOKEN",
    "BEARER",
    "OAUTH",
    "OAUTH_TOKEN",
    "CLIENT_SECRET",
    "CREDENTIAL",
    "CRED",
    "AUTHORIZATION",
    # Session and cookies
    "SESSION",
    "SESSION_ID",
    "SESSIONID",
    "SESSION_KEY",
    "SESSION_SECRET",
    "SESSION_TOKEN",
    "COOKIE",
    "COOKIES",
    "CSRF",
    "CSRFTOKEN",
    "CSRF_TOKEN",
    "XSRF",
    "XSRF_TOKEN",
    # JWT and signing
    "JWT",
    "JWT_SECRET",
    "JWT_TOKEN",
    "SIGNING_KEY",
    "SIGNATURE",
    # Database and connection strings
    "DATABASE_URL",
    "DATABASE_PASSWORD",
    "DB_URL",
    "DB_PASSWORD",
    "DB_PASS",
    "CONNECTION_STRING",
    "CONN_STR",
    "DSN",
    "MONGODB_URI",
    "MYSQL_PASSWORD",
    "POSTGRES_PASSWORD",
    "REDIS_PASSWORD",
    # Cloud providers
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SESSION_TOKEN",
    "AZURE_CLIENT_SECRET",
    "AZURE_TENANT_ID",
    "GCP_PRIVATE_KEY",
    "GOOGLE_API_KEY",
    "HEROKU_API_KEY",
    "DIGITALOCEAN_TOKEN",
    # Certificates and keys
    "CERTIFICATE",
    "CERT",
    "SSL_CERT",
    "TLS_CERT",
    "PRIVATE_KEY",
    "PUBLIC_KEY",
    "RSA_KEY",
    "SSH_KEY",
    "PEM",
    "KEY_FILE",
    "KEYFILE",
    "CLIENT_CERT",
    "CLIENT_KEY",
    "SERVER_KEY",
    # Payment and financial
    "STRIPE_KEY",
    "STRIPE_SECRET",
    "PAYMENT_TOKEN",
    "CREDIT_CARD",
    "CARD_NUMBER",
    "CVV",
    # Email and communication
    "SMTP_PASSWORD",
    "EMAIL_PASSWORD",
    "MAIL_PASSWORD",
    "SENDGRID_API_KEY",
    "MAILGUN_API_KEY",
    "TWILIO_AUTH_TOKEN",
    # Encryption and hashing
    "ENCRYPTION_KEY",
    "DECRYPT_KEY",
    "CIPHER",
    "CIPHER_KEY",
    "SALT",
    "HASH",
    "HMAC",
    "NONCE",
    # Network and headers
    "X_FORWARDED_FOR",
    "X_API_KEY",
    "X_AUTH_TOKEN",
    "X_ACCESS_TOKEN",
    # Generic sensitive patterns (will catch variations)
    "AUTH",
    "AUTHENTICATION",
    "PASSKEY",
    "PASSCODE",
    "PIN",
    "PINCODE",
    "MASTER_KEY",
    "ROOT_PASSWORD",
    "ADMIN_PASSWORD",
]


_CACHED_PATTERN: Pattern[str] | None = None

# Compiled regexes for identifier detection
_IDENTIFIER_CHARS_PATTERN = re.compile(r"^[\w]+$")
_CAMELCASE_SPLIT_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")

# Compiled regexes for character diversity detection (4x faster than loops)
_UPPER_PATTERN = re.compile(r"[A-Z]")
_LOWER_PATTERN = re.compile(r"[a-z]")
_DIGIT_PATTERN = re.compile(r"[0-9]")
_SPECIAL_PATTERN = re.compile(r"[+/=\-_]")

# Thresholds for identifier detection
MIN_TOKEN_LENGTH = 20  # Minimum length to check if token is an identifier
MIN_ENTROPY_FOR_CHECK = 3.0  # Minimum entropy to consider checking
MAX_ENTROPY_FOR_IDENTIFIER = 4.5  # Above this, almost certainly a secret
MIN_MEANINGFUL_WORD_LENGTH = 2  # Words shorter than this are filtered out
MAX_SHORT_WORDS_FOR_IDENTIFIER = (
    6  # Too many short words suggests random string
)
MIN_AVG_WORD_LENGTH = 4  # Average word length below this is suspicious
MAX_AVG_ENTROPY_WORD = 3.4
MAX_WORD_ENTROPY = 3.8  # Individual word entropy above this is suspicious
MIN_HEX_STRING_LENGTH = 20  # Hex strings longer than this are suspicious


def _is_programming_identifier(token: str, entropy: float) -> bool:
    """
    Check if a token looks like a programming identifier or number
    rather than a secret.

    This helps avoid false positives on long function/class names while still
    catching real secrets which typically have different patterns.

    Args:
        token: The string to check
        entropy: Pre-calculated entropy of the token

    Returns:
        True if the token appears to be a programming identifier
    """

    # Check if it's a file path or URL
    if "/" in token or "\\" in token:
        # Split by path separators and check component entropy
        # Real paths have low-entropy components (directory/file names)
        # while secrets with slashes tend to have high-entropy components

        components = re.split(r"[/\\]+", token)
        meaningful_components = [c for c in components if len(c) > 2]

        if meaningful_components:
            component_entropies = [
                _calculate_entropy(c) for c in meaningful_components
            ]
            avg_component_entropy = sum(component_entropies) / len(
                component_entropies
            )
            if avg_component_entropy < 3.0:
                return True

    # Check if it's a numeric literal using Python's int() or float() parser
    # This handles all valid Python numeric literals:
    # - Integers: 1000000, 1_000_000
    # - Hex: 0xDEADBEEF, 0xDEAD_BEEF
    # - Binary: 0b11110000, 0b1111_0000
    # - Octal: 0o777, 0o777_666
    # - Floats: 3.14159, 3.141_592_653
    # - Scientific: 1.23e45, 1.23e-45, 1_234.567_890e-10
    try:
        int(token, 0)
    except ValueError:
        # Not an integer, try float
        try:
            float(token)
        except ValueError:
            pass
        else:
            return True
    else:
        return True

    # Only check tokens that could be identifiers
    # (long enough, moderate entropy)
    if len(token) < MIN_TOKEN_LENGTH or entropy < MIN_ENTROPY_FOR_CHECK:
        return False

    # Very high entropy almost always indicates a secret,
    # not an identifier. This is an optimization and safety check -
    # real programming identifiers rarely exceed 4.2 entropy,
    # while many secrets are above this threshold
    if entropy > MAX_ENTROPY_FOR_IDENTIFIER:
        return False

    # Quick check: programming identifiers only contain \w (letters/digits/_)
    if not _IDENTIFIER_CHARS_PATTERN.match(token):
        # Contains special characters, definitely not an identifier
        return False

    # Split token into words by both underscores and camelCase boundaries
    # First split by underscores
    parts = token.split("_")

    # Then split each part by camelCase boundaries
    words = []
    for part in parts:
        if part:
            # For same-caps parts, keep as is (e.g., "EMAIL" or "pattern")
            if (part.isupper() or part.islower()) and len(part) > 1:
                words.append(part)
            else:
                # Split camelCase: insert space before uppercase letters
                # (except at start). This handles: camelCase, PascalCase,
                # HTTPSConnection, etc.
                camel_words = _CAMELCASE_SPLIT_PATTERN.sub(" ", part).split()
                words.extend(camel_words)

    # Filter out very short words and pure numbers
    meaningful_words = [
        w
        for w in words
        if len(w) >= MIN_MEANINGFUL_WORD_LENGTH and not w.isdigit()
    ]

    if not meaningful_words:
        # No meaningful words found - suspicius, let's say it's not
        # an identifier
        return False

    # If we have too many short "words", it's likely a random string being
    # incorrectly split (like base64)
    avg_word_len = sum(len(w) for w in meaningful_words) / len(
        meaningful_words
    )
    if (
        len(meaningful_words) > MAX_SHORT_WORDS_FOR_IDENTIFIER
        and avg_word_len < MIN_AVG_WORD_LENGTH
    ):
        # Too many short words - suspicious
        return False

    # Calculate average entropy of the meaningful words
    word_entropies = [_calculate_entropy(w) for w in meaningful_words]
    avg_entropy = sum(word_entropies) / len(word_entropies)

    # Very high average entropy suggests random strings
    if avg_entropy > MAX_AVG_ENTROPY_WORD:
        return False

    # Any single word with very high entropy is suspicious
    if any(
        _calculate_entropy(word) > MAX_WORD_ENTROPY
        for word in meaningful_words
    ):
        return False

    # Passed all checks - looks like a programming identifier
    return True


def _calculate_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string.

    Shannon entropy measures the randomness/unpredictability of a string.
    Higher entropy indicates more randomness (likely a generated secret).

    Entropy ranges and what they typically indicate:
    - 0.0-1.0: Very low - repeated characters ("aaaa", "1111")
    - 1.0-2.5: Low - simple patterns, dictionary words ("password", "admin")
    - 2.5-3.5: Medium - weak passwords, predictable strings ("password123")
    - 3.5-4.0: Medium-high - better passwords ("MyP@ssw0rd")
    - 4.0-4.5: High - likely generated/random ("aB3dE5fG7h")
    - 4.5-5.0: Very high - strongly random ("base64 tokens", "UUIDs")
    - 5.0+: Maximum randomness - cryptographic keys, tokens

    For context:
    - English text: ~2.5-3.5
    - Hex strings: ~4.0
    - Base64: ~4.5-5.0
    - Random bytes: ~5.0-6.0
    """

    n = len(s)
    if n == 0:
        return 0.0
    counts = collections.Counter(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _create_combined_pattern() -> Pattern[str]:
    """Create and cache the combined pattern for single-pass scanning.

    Matches various formats:
    - Email addresses
    - FIELD:'value' or FIELD:"value" (quoted)
    - FIELD: value (YAML style, unquoted)
    - FIELD=value (.env style, unquoted)
    - "FIELD": "value" (JSON style)
    - export FIELD=value (shell export)
    - High-entropy tokens
    """
    global _CACHED_PATTERN

    if _CACHED_PATTERN is not None:
        return _CACHED_PATTERN

    # Build sensitive field patterns with hyphen variations
    sensitive_patterns = set(
        SENSITIVE_PATTERNS
        + ([pat.replace("_", "-") for pat in SENSITIVE_PATTERNS if "_" in pat])
    )
    patterns = "|".join(re.escape(p) for p in sensitive_patterns)

    # Create a single comprehensive regex that matches all types at once
    combined_pattern = rf"""
        (?P<email>
            # Email pattern
            \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{{2,}}\b
        )
        |
        (?:
            # Quoted sensitive values
            (?:^|[^a-zA-Z0-9_]|["']\s*|{{\s*|,\s*)
            (?P<quoted_field>{patterns})
            (?:["']?\s*[:=]\s*|"\s*:\s*)
            ["'](?P<quoted_value>[^"']+)["']
        )
        |
        (?:
            # Unquoted sensitive values
            (?:^|^\s*[-*]\s+|[^a-zA-Z0-9_]|^\s*export\s+)
            (?P<unquoted_field>{patterns})
            \s*[:=]\s*
            (?!["'])(?P<unquoted_value>[^\n\r#,;{{}}[\]]+)
        )
        |
        (?P<path>
            # Path-like patterns that should not be treated as secrets
            # Matches paths with forward slashes, backslashes, or escaped
            # spaces
            (?:
                # Unix/URL paths starting with /, ./, ~/, http://, https://
                # Can be preceded by whitespace or quotes
                (?:^|(?<=[\s"']))(?:/|\\./|~/|[a-zA-Z\+\-_]{2, 20}://)
                (?:[A-Za-z0-9._\-]+(?:[/\\]|\\\ ))*[A-Za-z0-9._\-]+
            )
            |
            (?:
                # Windows paths like C:\, D:\, etc.
                # Can be preceded by whitespace or quotes
                (?:^|(?<=[\s"']))[A-Za-z]:[/\\]
                (?:[A-Za-z0-9._\-]+(?:[/\\]|\\\ ))*[A-Za-z0-9._\-]+
            )
            |
            (?:
                # Paths with escaped spaces (common in shell contexts)
                (?:[A-Za-z0-9._\-/\\]+(?:\\\ )+[A-Za-z0-9._\-/\\]+)+
            )
        )
        |
        (?P<token>
            # High-entropy tokens (no forward slash to avoid matching paths)
            \b[A-Za-z0-9+=\-_]{{20,}}\b
        )
    """

    _CACHED_PATTERN = re.compile(combined_pattern, re.I | re.M | re.X)
    return _CACHED_PATTERN


def scan_and_replace(
    text: str,
    /,
    *,
    entropy_threshold: float = 3.5,
    placeholder_mapping: dict[str, str] | None = None,
    # Special args for tests:
    __skip_is_identifier_check: bool = False,
) -> tuple[str, dict[str, str]]:
    """
    Scan text for sensitive data and replace with placeholders.

    Args:
        text: The text to scan
        entropy_threshold: Minimum entropy for potential secret detection.
        placeholder_counter_start: Starting value for placeholder counter.

    Returns:
        Tuple of (sanitized_text, placeholder_mapping) where:
        - sanitized_text: Input with secrets replaced by placeholders
        - placeholder_mapping: Dict mapping placeholders to original values
    """

    index: dict[str, str] = {}

    if placeholder_mapping is not None:
        index = {v: k for k, v in placeholder_mapping.items()}
        placeholder_mapping = placeholder_mapping.copy()
    else:
        placeholder_mapping = {}

    placeholder_counter = len(placeholder_mapping) + 1

    pattern = _create_combined_pattern()

    def replace_match(match: re.Match[str]) -> str:
        nonlocal placeholder_counter

        if email := match.group("email"):
            if email in index:
                return index[email]

            placeholder = f"placeholder{placeholder_counter}@example.com"
            placeholder_mapping[placeholder] = email
            placeholder_counter += 1
            return placeholder

        if field_name := match.group("quoted_field"):
            value = match.group("quoted_value")

            if value:
                if value in index:
                    return match.group(0).replace(value, index[value])

                ident = field_name.upper().replace("-", "_")
                placeholder = f"PLACEHOLDER_{ident}_{placeholder_counter}"
                placeholder_mapping[placeholder] = value
                placeholder_counter += 1
                return match.group(0).replace(value, placeholder)

        if field_name := match.group("unquoted_field"):
            value = match.group("unquoted_value").strip()

            if value:
                if value in index:
                    return match.group(0).replace(value, index[value])

                ident = field_name.upper().replace("-", "_")
                placeholder = f"PLACEHOLDER_{ident}_{placeholder_counter}"
                placeholder_mapping[placeholder] = value
                placeholder_counter += 1
                return match.group(0).replace(value, placeholder)

        # Path patterns should be validated before being left unchanged
        if path := match.group("path"):
            if _calculate_entropy(path) < MAX_ENTROPY_FOR_IDENTIFIER:
                # Split by path separators and check component entropy
                # Real paths have low-entropy components (directory/file names)
                # while secrets looking like paths would have high entropy
                components = re.split(r"[/\\]+", path)
                # Filter out empty components and very short ones
                meaningful_components = [
                    c
                    for c in components
                    if len(c) >= MIN_MEANINGFUL_WORD_LENGTH
                ]

                if meaningful_components:
                    component_entropies = [
                        _calculate_entropy(c) for c in meaningful_components
                    ]
                    avg_component_entropy = sum(component_entropies) / len(
                        component_entropies
                    )

                    max_component_entropy = max(component_entropies)

                    # Paths typically have low-entropy components
                    # Real paths: avg < 3.2 and no single component > 4.0
                    # This allows for some random parts (like temp files)
                    # but catches secrets
                    if (
                        avg_component_entropy < MAX_AVG_ENTROPY_WORD
                        and max_component_entropy < MAX_WORD_ENTROPY
                    ):
                        return match.group(0)

            if path in index:
                return index[path]

            placeholder = f"PLACEHOLDER_PATH_{placeholder_counter}"
            placeholder_mapping[placeholder] = path
            placeholder_counter += 1
            return placeholder

        # Check if it's a high-entropy token
        if token := match.group("token"):
            entropy = _calculate_entropy(token)

            if not __skip_is_identifier_check and _is_programming_identifier(
                token, entropy
            ):
                return token

            # Calculate character diversity for secret detection
            has_upper = bool(_UPPER_PATTERN.search(token))
            has_lower = bool(_LOWER_PATTERN.search(token))
            has_digit = bool(_DIGIT_PATTERN.search(token))
            has_special = bool(_SPECIAL_PATTERN.search(token))

            char_diversity = sum(
                [has_upper, has_lower, has_digit, has_special]
            )

            if (
                (entropy >= entropy_threshold and char_diversity >= 2)
                or (has_special and len(token) >= 20)  # base64-like
                or (len(token) >= 32 and char_diversity >= 2)  # hex-like
            ):
                if token in index:
                    return index[token]

                placeholder = f"PLACEHOLDER_TOKEN_{placeholder_counter}"
                placeholder_mapping[placeholder] = token
                placeholder_counter += 1
                return placeholder

        return match.group(0)

    result = pattern.sub(replace_match, text)
    return result, placeholder_mapping
