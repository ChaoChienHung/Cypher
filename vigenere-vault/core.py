"""
Core Cryptography and Vault Engine for Vigenère Vault.
Provides backward-compatible encryption, decryption, and multi-key vault management.
"""

from dataclasses import dataclass
import hashlib
from pathlib import Path
import secrets
from typing import Dict, List, Optional, Union

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
    # Using secrets for cryptographic randomness while keeping 8-digit format
    return str(secrets.randbelow(90000000) + 10000000)


def encrypt_secret_line(key: str, secret: str, custom_salt: Optional[str] = None) -> str:
    """
    Encrypt a single secret with a master key.
    
    Returns:
        Formatted file line string: 'RandomNumber(8) + Encrypted(Key + Secret) + \\n'
    """
    salt = custom_salt if custom_salt is not None else generate_salt_8()
    hashed_string = get_hashed_string(salt + key)
    encrypted_body = vigenere_cipher(key + secret, hashed_string, mode=True)
    return salt + encrypted_body + '\n'


def decrypt_secret_line(line: str, key: str) -> Optional[str]:
    """
    Attempt to decrypt a vault line using the given key.
    
    Returns:
        The decrypted secret text if the key matches, or None if the key is incorrect.
    """
    clean_line = line.rstrip('\r\n')
    if len(clean_line) < 8:
        return None

    salt = clean_line[:8]
    encrypted_body = clean_line[8:]
    hashed_string = get_hashed_string(salt + key)
    decrypted_body = vigenere_cipher(encrypted_body, hashed_string, mode=False)

    if decrypted_body.startswith(key):
        # Safely remove prefix (avoids the legacy lstrip bug)
        return decrypted_body[len(key):]
    return None


@dataclass
class VaultEntry:
    """Represents a successfully decrypted secret from a vault file."""
    line_number: int  # 1-based index in the vault file
    salt: str
    secret: str
    raw_line: str


class VigenereVault:
    """
    High-level vault manager handling file I/O, multi-key querying,
    safe additions, deletions, and exports.
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

    def add_secret(self, key: str, secret: str) -> VaultEntry:
        """Append a new encrypted secret to the vault."""
        self.ensure_vault_exists()
        line = encrypt_secret_line(key, secret)
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(line)

        # Count total lines to determine line number
        with open(self.path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)

        return VaultEntry(
            line_number=total_lines,
            salt=line[:8],
            secret=secret,
            raw_line=line
        )

    def add_secrets_batch(self, key: str, secrets_list: List[str]) -> List[VaultEntry]:
        """Add multiple secrets under the same key in a single batch."""
        entries = []
        for s in secrets_list:
            clean_s = s.strip()
            if clean_s:
                entries.append(self.add_secret(key, clean_s))
        return entries

    def query_secrets(self, key: str) -> List[VaultEntry]:
        """
        Scan the vault file and return all secrets decryptable with the provided key.
        Preserves original line numbers so duplicates can be disambiguated.
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
                secret = decrypt_secret_line(line, key)
                if secret is not None:
                    results.append(VaultEntry(
                        line_number=idx,
                        salt=salt,
                        secret=secret,
                        raw_line=line
                    ))
        return results

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
        """Export decrypted secrets to TXT or Markdown format."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        fmt = fmt.lower()
        with open(out_p, 'w', encoding='utf-8') as f:
            if fmt == "md" or fmt == "markdown":
                f.write(f"# Decrypted Secrets (Key: {key})\n\n")
                f.write(f"> Total entries: {len(entries)}\n\n")
                for i, entry in enumerate(entries, start=1):
                    f.write(f"{i}. `{entry.secret}`\n")
            else:
                f.write(f"Key: {key}\n")
                f.write("=" * 40 + "\n")
                for i, entry in enumerate(entries, start=1):
                    f.write(f"{i}. {entry.secret}\n")
                f.write("\n")

        return out_p
