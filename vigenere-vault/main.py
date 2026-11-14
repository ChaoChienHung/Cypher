#!/usr/bin/env python3
"""
Vigenère Vault - Main Console Entrypoint.
Optimized for robustness, error handling, and unified architecture with core.py.
"""

from pathlib import Path
import sys

# Ensure local directory is in path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core import (
    VigenereVault,
    get_hashed_string,
    vigenere_cipher,
    encrypt_secret_line,
    decrypt_secret_line,
)

# Backward-compatible function aliases
getHashedstring = get_hashed_string
vigenereCipher = vigenere_cipher


def run_legacy_interactive():
    default_vault_file = "Secrets.txt"
    # Resolve default path: look locally or in parent dir
    if not Path(default_vault_file).exists() and (current_dir.parent / default_vault_file).exists():
        default_vault_file = str(current_dir.parent / default_vault_file)

    while True:
        print("\n" + "=" * 48)
        print("🔐 Vigenère Vault - Console Manager")
        print("=" * 48)
        print("Please enter your command:")
        print("(1) Create Encoded Text")
        print("(2) Decode Encoded Text")
        print("(3) Modify Encoded Text")
        print("(4) Launch Graphical UI (GUI)")
        print("(5) Exit")
        print("=" * 48)

        choice = input("Your choice (1-5): ").strip()

        if choice == "1":
            filename = input("Enter vault filename [Secrets.txt]: ").strip() or "Secrets.txt"
            if not filename.endswith(".txt"):
                filename += ".txt"
            vault = VigenereVault(filename)
            key = input("Please enter your Key: ").strip()
            if not key:
                print("[!] Key cannot be empty.")
                continue

            count = 0
            while True:
                secret = input(f"Please enter Secret #{count + 1}: ").strip()
                if secret:
                    entry = vault.add_secret(key, secret)
                    count += 1
                    print(f"[✓] Encrypted and saved to line {entry.line_number} (Salt: {entry.salt})")

                cont = input("Do you want to continue with the same Key? (1) Yes, (2) No: ").strip()
                if cont == "2":
                    break

            print(f"[+] Total {count} secrets written to {vault.path.name}.")

        elif choice == "2":
            filename = input(f"Enter vault filename [{default_vault_file}]: ").strip() or default_vault_file
            vault = VigenereVault(filename)
            if not vault.exists():
                print(f"[!] Vault file does not exist: {vault.path}")
                continue

            key = input("Please enter the Key of the Secrets: ").strip()
            entries = vault.query_secrets(key)

            if not entries:
                print(f"[!] No secrets found matching key '{key}'.")
                continue

            print(f"\n[+] Found {len(entries)} secrets.")
            print("Please choose how to display your decoded Secrets:")
            print("(1) Through Console")
            print("(2) Export to Text File (decodedSecrets.txt)")
            print("(3) Export to Markdown File (decodedSecrets.md)")
            out_choice = input("Select (1-3) [1]: ").strip() or "1"

            if out_choice == "1":
                print("\n" + "=" * 52)
                print(f"Below are the Secrets encoded with Key: {key}")
                print("=" * 52)
                for i, entry in enumerate(entries, start=1):
                    print(f"{i}. (Line {entry.line_number} | Salt: {entry.salt}) -> {entry.secret}")
                print("=" * 52)

            elif out_choice == "2":
                out_path = vault.export_entries(entries, key, "decodedSecrets.txt", fmt="txt")
                print(f"[✓] Successfully exported to: {out_path.resolve()}")

            elif out_choice == "3":
                out_path = vault.export_entries(entries, key, "decodedSecrets.md", fmt="md")
                print(f"[✓] Successfully exported to: {out_path.resolve()}")

        elif choice == "3":
            filename = input(f"Enter vault filename [{default_vault_file}]: ").strip() or default_vault_file
            vault = VigenereVault(filename)

            while True:
                print("\nHow do you want to modify your Secrets:")
                print("(1) Add Secrets")
                print("(2) Remove Secrets")
                print("(0) Back to Main Menu")
                sub_choice = input("Select (0-2): ").strip()

                if sub_choice == "1":
                    key = input("Please enter your Key: ").strip()
                    if not key:
                        print("[!] Key cannot be empty.")
                        continue
                    while True:
                        secret = input("Please enter your Secret: ").strip()
                        if secret:
                            entry = vault.add_secret(key, secret)
                            print(f"[✓] Added to line {entry.line_number} (Salt: {entry.salt})")
                        cont = input("Continue adding with same Key? (1) Yes, (2) No: ").strip()
                        if cont == "2":
                            break

                elif sub_choice == "2":
                    key = input("Please enter the Key of the Secrets: ").strip()
                    entries = vault.query_secrets(key)
                    if not entries:
                        print(f"[!] No secrets found for Key '{key}'.")
                        continue

                    print("\n--- Current Secrets under this Key ---")
                    for i, entry in enumerate(entries, start=1):
                        print(f"{i}. (Line {entry.line_number}) {entry.secret}")

                    print("\nPlease choose the Secret '#' you want to remove (or 0 to cancel):")
                    rem_input = input("Target number: ").strip()
                    try:
                        rem_idx = int(rem_input)
                        if 1 <= rem_idx <= len(entries):
                            target_entry = entries[rem_idx - 1]
                            confirm = input(f"Are you sure you want to delete '{target_entry.secret}'? (y/n): ")
                            if confirm.lower().startswith('y'):
                                vault.delete_by_line_numbers([target_entry.line_number])
                                print(f"[✓] Successfully removed line {target_entry.line_number}.")
                            else:
                                print("[*] Deletion cancelled.")
                        elif rem_idx == 0:
                            print("[*] Cancelled.")
                        else:
                            print("[!] Invalid index.")
                    except ValueError:
                        print("[!] Please enter a valid number.")

                elif sub_choice == "0":
                    break

        elif choice == "4":
            print("[*] Launching Graphical User Interface (GUI)...")
            try:
                import gui
                gui.main()
            except Exception as e:
                print(f"[!] Failed to launch GUI: {e}")

        elif choice == "5":
            print("Exiting... Stay safe!")
            break


def main():
    if "--gui" in sys.argv:
        import gui
        gui.main()
    elif "--cli" in sys.argv:
        import cli
        # Remove --cli from argv before passing to cli parser
        sys.argv.remove("--cli")
        cli.main()
    else:
        run_legacy_interactive()


if __name__ == "__main__":
    main()
