"""
Core Cryptography and Vault Engine for Vigenère Vault.
Provides backward-compatible encryption, decryption, and multi-key vault management
with support for structured properties (title, tags, category, timestamp) and filtering.
"""

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path
import secrets
from typing import Dict, List, Optional, Set, Union

# 33-symbol extended special character set (strictly compatible with legacy cipher)
SPECIAL_SYMBOLS: List[str] = [
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
    '-', '_', '=', '+', '[', ']', '{', '}', '\\', '|',
    ';', ':', "'", '"', ',', '.', '/', '<', '>', '?',
    '~', '`', ' ',
]


def get_hashed_string(key: str) -> str:
    """Generate SHA-256 hexadecimal hash string for a given key string."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(key.encode('utf-8'))
    return sha256_hash.hexdigest()


def vigenere_cipher(input_string: str, key_hex: str, mode: bool = True) -> str:
    """
    Encrypt or decrypt an input string using dynamic hex shifting (Extended Vigenère).
    
    Args:
        input_string: Plaintext or ciphertext string.
        key_hex: Hexadecimal string (usually 64 chars from SHA-256) used for shift steps.
        mode: True for encryption, False for decryption.
    """
    key_length = len(key_hex)
    key_ints = [int(char, 16) for char in key_hex]
    sym_len = len(SPECIAL_SYMBOLS)
    result = []

    for i, char in enumerate(input_string):
        shift = key_ints[i % key_length]

        if char.isalpha():
            start = ord('a') if char.islower() else ord('A')
            if not mode:  # Decrypt
                new_char = chr(start + (ord(char) - start - shift) % 26)
            else:  # Encrypt
                new_char = chr(start + (ord(char) - start + shift) % 26)
            result.append(new_char)

        elif char in SPECIAL_SYMBOLS:
            idx = SPECIAL_SYMBOLS.index(char)
            if not mode:  # Decrypt
                new_char = SPECIAL_SYMBOLS[(idx - shift) % sym_len]
            else:  # Encrypt
                new_char = SPECIAL_SYMBOLS[(idx + shift) % sym_len]
            result.append(new_char)

        else:
            result.append(char)

    return ''.join(result)


def generate_salt_8() -> str:
    """Generate a cryptographically secure 8-digit decimal salt string (10000000-99999999)."""
    return str(secrets.randbelow(90000000) + 10000000)


@dataclass
class VaultEntry:
    """
    Represents a successfully decrypted secret from a vault file.
    Supports structured properties (title, tags, category, created_at)
    while remaining 100% backward-compatible with legacy plain text entries.
    """
    line_number: int  # 1-based index in the vault file
    salt: str
    secret: str
    raw_line: str
    title: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = "General"
    created_at: str = ""

    def matches_filter(
        self,
        tag: Optional[str] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> bool:
        """Check if this entry matches filtering criteria."""
        if tag and tag.lower() not in [t.lower() for t in self.tags]:
            return False
        if category and category.lower() != "all" and self.category.lower() != category.lower():
            return False
        if search_query:
            q = search_query.lower()
            in_secret = q in self.secret.lower()
            in_title = q in self.title.lower()
            in_tags = any(q in t.lower() for t in self.tags)
            in_cat = q in self.category.lower()
            if not (in_secret or in_title or in_tags or in_cat):
                return False
        return True


def serialize_payload(
    secret: str,
    title: str = "",
    tags: Optional[List[str]] = None,
    category: str = "General",
    created_at: Optional[str] = None
) -> str:
    """Pack structured secret properties into a JSON string payload."""
    clean_tags = [t.strip() for t in (tags or []) if t.strip()]
    ts = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "v": 2,
        "title": title.strip(),
        "secret": secret,
        "tags": clean_tags,
        "category": category.strip() or "General",
        "created_at": ts
    }
    return json.dumps(payload, ensure_ascii=False)


def parse_payload(raw_text: str) -> Dict:
    """
    Parse decrypted payload text.
    If valid JSON object with 'secret', returns dict of properties.
    Otherwise falls back seamlessly to legacy raw string.
    """
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict) and "secret" in data:
            return {
                "title": data.get("title", ""),
                "secret": str(data.get("secret", "")),
                "tags": list(data.get("tags", [])),
                "category": data.get("category", "General"),
                "created_at": data.get("created_at", "")
            }
    except Exception:
        pass

    # Legacy fallback
    return {
        "title": "",
        "secret": raw_text,
        "tags": [],
        "category": "General",
        "created_at": ""
    }


def encrypt_secret_line(
    key: str,
    secret: str,
    title: str = "",
    tags: Optional[List[str]] = None,
    category: str = "General",
    custom_salt: Optional[str] = None
) -> str:
    """
    Encrypt a secret with optional properties using master key.
    
    Returns:
        Formatted file line: 'RandomNumber(8) + Encrypted(Key + Payload) + \\n'
    """
    salt = custom_salt if custom_salt is not None else generate_salt_8()
    payload = serialize_payload(secret, title=title, tags=tags, category=category)
    hashed_string = get_hashed_string(salt + key)
    encrypted_body = vigenere_cipher(key + payload, hashed_string, mode=True)
    return salt + encrypted_body + '\n'


def decrypt_secret_line(line: str, key: str) -> Optional[Dict]:
    """
    Attempt to decrypt a vault line using the given key.
    
    Returns:
        Dict with keys (title, secret, tags, category, created_at) if valid key, else None.
    """
    clean_line = line.rstrip('\r\n')
    if len(clean_line) < 8:
        return None

    salt = clean_line[:8]
    encrypted_body = clean_line[8:]
    hashed_string = get_hashed_string(salt + key)
    decrypted_body = vigenere_cipher(encrypted_body, hashed_string, mode=False)

    if decrypted_body.startswith(key):
        raw_payload = decrypted_body[len(key):]
        return parse_payload(raw_payload)
    return None


class VigenereVault:
    """
    High-level vault manager handling file I/O, multi-key querying,
    property metadata, safe additions, deletions, filtering and exports.
    """

    def __init__(self, vault_path: Union[str, Path] = "Secrets.txt"):
        self.path = Path(vault_path)

    def exists(self) -> bool:
        return self.path.exists() and self.path.is_file()

    def ensure_vault_exists(self) -> None:
        """Create the vault file if it doesn't already exist."""
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()

    def add_secret(
        self,
        key: str,
        secret: str,
        title: str = "",
        tags: Optional[List[str]] = None,
        category: str = "General"
    ) -> VaultEntry:
        """Append a new encrypted secret with properties to the vault."""
        self.ensure_vault_exists()
        line = encrypt_secret_line(key, secret, title=title, tags=tags, category=category)
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(line)

        # Count total lines to determine line number
        with open(self.path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)

        clean_tags = [t.strip() for t in (tags or []) if t.strip()]
        return VaultEntry(
            line_number=total_lines,
            salt=line[:8],
            secret=secret,
            raw_line=line,
            title=title.strip(),
            tags=clean_tags,
            category=category.strip() or "General",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def add_secrets_batch(self, key: str, secrets_list: List[str]) -> List[VaultEntry]:
        """Add multiple simple secrets under the same key in a single batch."""
        entries = []
        for s in secrets_list:
            clean_s = s.strip()
            if clean_s:
                entries.append(self.add_secret(key, clean_s))
        return entries

    def query_secrets(
        self,
        key: str,
        filter_tag: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_text: Optional[str] = None
    ) -> List[VaultEntry]:
        """
        Scan the vault file and return all secrets decryptable with the provided key.
        Applies optional filters (tag, category, search query).
        """
        if not self.exists():
            return []

        results: List[VaultEntry] = []
        with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
            for idx, line in enumerate(f, start=1):
                clean_line = line.rstrip('\r\n')
                if len(clean_line) < 8:
                    continue
                salt = clean_line[:8]
                parsed = decrypt_secret_line(line, key)
                if parsed is not None:
                    entry = VaultEntry(
                        line_number=idx,
                        salt=salt,
                        secret=parsed["secret"],
                        raw_line=line,
                        title=parsed["title"],
                        tags=parsed["tags"],
                        category=parsed["category"],
                        created_at=parsed["created_at"]
                    )
                    if entry.matches_filter(filter_tag, filter_category, filter_text):
                        results.append(entry)
        return results

    def get_all_tags(self, entries: List[VaultEntry]) -> List[str]:
        """Extract all unique tags sorted alphabetically from a list of entries."""
        tags_set: Set[str] = set()
        for e in entries:
            for t in e.tags:
                if t.strip():
                    tags_set.add(t.strip())
        return sorted(list(tags_set))

    def get_all_categories(self, entries: List[VaultEntry]) -> List[str]:
        """Extract all unique categories from a list of entries."""
        cats: Set[str] = {e.category for e in entries if e.category}
        return sorted(list(cats))

    def delete_by_line_numbers(self, line_numbers_to_delete: List[int]) -> int:
        """
        Safely remove specific lines from the vault file by their line numbers.
        Returns the count of deleted lines.
        """
        if not self.exists():
            return 0

        target_set = set(line_numbers_to_delete)
        retained_lines: List[str] = []
        deleted_count = 0

        with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
            for idx, line in enumerate(f, start=1):
                if idx in target_set:
                    deleted_count += 1
                else:
                    retained_lines.append(line)

        with open(self.path, 'w', encoding='utf-8') as f:
            f.writelines(retained_lines)

        return deleted_count

    def export_entries(
        self,
        entries: List[VaultEntry],
        key: str,
        output_path: Union[str, Path],
        fmt: str = "txt"
    ) -> Path:
        """Export decrypted secrets with properties to TXT or Markdown format."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        fmt = fmt.lower()
        with open(out_p, 'w', encoding='utf-8') as f:
            if fmt in ["md", "markdown"]:
                f.write(f"# Decrypted Secrets (Key: {key})\n\n")
                f.write(f"> Total entries: {len(entries)}\n\n")
                f.write("| # | Title | Category | Tags | Secret | Created |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
                for i, entry in enumerate(entries, start=1):
                    tags_str = " ".join([f"`#{t}`" for t in entry.tags]) if entry.tags else "-"
                    title_str = entry.title or "(Untitled)"
                    f.write(f"| {i} | {title_str} | {entry.category} | {tags_str} | `{entry.secret}` | {entry.created_at} |\n")
            else:
                f.write(f"Key: {key}\n")
                f.write("=" * 60 + "\n")
                for i, entry in enumerate(entries, start=1):
                    title_part = f"[{entry.title}] " if entry.title else ""
                    cat_part = f"({entry.category}) " if entry.category != "General" else ""
                    tags_part = f" #{' #'.join(entry.tags)}" if entry.tags else ""
                    f.write(f"{i}. {title_part}{cat_part}{entry.secret}{tags_part} (Line {entry.line_number})\n")
                f.write("\n")

        return out_p
