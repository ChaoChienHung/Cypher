#!/usr/bin/env python3
"""
Enhanced CLI for Vigenère Vault.
Supports rich interactive menus, password masking, tabular displays,
structured properties (title, tags, category), and filter/search subcommands.
"""

import argparse
import getpass
import os
from pathlib import Path
import sys
from typing import List, Optional

# Ensure local core module is importable
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core import VigenereVault, VaultEntry

# Check for rich library support
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None


def print_info(msg: str):
    if HAS_RICH:
        console.print(f"[cyan]ℹ {msg}[/cyan]")
    else:
        print(f"[*] {msg}")


def print_success(msg: str):
    if HAS_RICH:
        console.print(f"[bold green]✔ {msg}[/bold green]")
    else:
        print(f"[+] {msg}")


def print_warning(msg: str):
    if HAS_RICH:
        console.print(f"[bold yellow]⚠ {msg}[/bold yellow]")
    else:
        print(f"[!] {msg}")


def print_error(msg: str):
    if HAS_RICH:
        console.print(f"[bold red]✖ {msg}[/bold red]")
    else:
        print(f"[-] {msg}")


def display_entries_table(entries: List[VaultEntry], key: str, filter_info: str = ""):
    """Render decrypted entries in a clear, structured table."""
    if not entries:
        info_suffix = f" (Filter: {filter_info})" if filter_info else ""
        print_warning(f"No secrets found matching the key and criteria{info_suffix}.")
        return

    title_text = f"Decrypted Secrets (Key: {key})"
    if filter_info:
        title_text += f" | Filter: {filter_info}"

    if HAS_RICH:
        table = Table(
            title=title_text,
            show_header=True,
            header_style="bold magenta",
            border_style="dim"
        )
        table.add_column("#", justify="right", style="cyan", width=4)
        table.add_column("Title", style="bold white", width=18)
        table.add_column("Category", style="yellow", width=10)
        table.add_column("Tags", style="cyan", width=16)
        table.add_column("Secret Plaintext", style="bold green")
        table.add_column("Line", justify="center", style="dim", width=6)

        for idx, entry in enumerate(entries, start=1):
            title_display = entry.title or "(Untitled)"
            tags_display = " ".join([f"#{t}" for t in entry.tags]) if entry.tags else "-"
            table.add_row(
                str(idx),
                title_display,
                entry.category,
                tags_display,
                entry.secret,
                f"L{entry.line_number}"
            )

        console.print(table)
    else:
        print(f"\n=== {title_text} ===")
        for idx, entry in enumerate(entries, start=1):
            title_part = f"[{entry.title}] " if entry.title else ""
            cat_part = f"({entry.category}) " if entry.category != "General" else ""
            tags_part = f" #{' #'.join(entry.tags)}" if entry.tags else ""
            print(f"[{idx}] (Line {entry.line_number}) {title_part}{cat_part}{entry.secret}{tags_part}")
        print("=" * 50 + "\n")


def get_master_key(provided_key: Optional[str] = None) -> str:
    """Retrieve key from argument, environment variable, or secure prompt."""
    if provided_key:
        return provided_key
    env_key = os.environ.get("VAULT_KEY")
    if env_key:
        return env_key
    while True:
        k = getpass.getpass("Enter Master Key (hidden): ")
        if k:
            return k
        print_warning("Key cannot be empty.")


def resolve_vault_path(path_str: Optional[str] = None) -> Path:
    """Find vault file with sensible defaults."""
    if path_str:
        return Path(path_str).resolve()
    # Default search order: ./Secrets.txt -> ../Secrets.txt
    local_p = Path("Secrets.txt")
    if local_p.exists():
        return local_p.resolve()
    parent_p = Path(__file__).resolve().parent.parent / "Secrets.txt"
    if parent_p.exists():
        return parent_p.resolve()
    return local_p.resolve()


# ==========================================
# Interactive Mode
# ==========================================
def interactive_menu(vault_path: Path):
    vault = VigenereVault(vault_path)
    if HAS_RICH:
        console.print(Panel.fit(
            f"[bold cyan]🔐 Vigenère Vault - Interactive Terminal[/bold cyan]\n"
            f"[dim]Active Vault: {vault.path}[/dim]\n"
            f"[dim]Status: {'Existing' if vault.exists() else 'New File'}[/dim]",
            border_style="cyan"
        ))
    else:
        print("=" * 50)
        print(f"  Vigenère Vault - Interactive CLI")
        print(f"  Vault File: {vault.path}")
        print("=" * 50)

    while True:
        print()
        if HAS_RICH:
            console.print("[bold]Menu Options:[/bold]")
            console.print("  [cyan]1[/cyan]. Query & Filter Secrets (All / By Tag / By Category)")
            console.print("  [cyan]2[/cyan]. Add New Secret (with Title & Tags)")
            console.print("  [cyan]3[/cyan]. Batch Add Secrets (Simple)")
            console.print("  [cyan]4[/cyan]. Delete Secret")
            console.print("  [cyan]5[/cyan]. Change Vault File")
            console.print("  [cyan]0[/cyan]. Exit")
            choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4", "5"], default="1")
        else:
            print("1. Query & Filter Secrets")
            print("2. Add New Secret (with Title & Tags)")
            print("3. Batch Add Secrets (Simple)")
            print("4. Delete Secret")
            print("5. Change Vault File")
            print("0. Exit")
            choice = input("\nSelect option (0-5) [1]: ").strip() or "1"

        if choice == "0":
            print_info("Exiting Vigenère Vault. Stay secure!")
            break

        elif choice == "1":
            key = get_master_key()
            all_entries = vault.query_secrets(key)
            if not all_entries:
                print_warning(f"No secrets found matching the key in vault.")
                continue

            available_tags = vault.get_all_tags(all_entries)
            available_cats = vault.get_all_categories(all_entries)

            print_info(f"Unlocked {len(all_entries)} secrets.")
            if available_tags:
                print_info(f"Available tags: {', '.join(['#' + t for t in available_tags])}")

            # Optional filter prompt
            filter_prompt = input("Filter by (1: Show All, 2: Tag, 3: Category, 4: Keyword Search) [1]: ").strip() or "1"
            filter_tag, filter_cat, filter_q = None, None, None
            filter_label = ""

            if filter_prompt == "2":
                tag_in = input(f"Enter Tag to filter ({'/'.join(available_tags)}): ").strip().lstrip("#")
                if tag_in:
                    filter_tag = tag_in
                    filter_label = f"Tag=#{tag_in}"
            elif filter_prompt == "3":
                cat_in = input(f"Enter Category to filter ({'/'.join(available_cats)}): ").strip()
                if cat_in:
                    filter_cat = cat_in
                    filter_label = f"Category={cat_in}"
            elif filter_prompt == "4":
                q_in = input("Enter search keyword: ").strip()
                if q_in:
                    filter_q = q_in
                    filter_label = f"Keyword='{q_in}'"

            filtered_entries = [e for e in all_entries if e.matches_filter(filter_tag, filter_cat, filter_q)]
            display_entries_table(filtered_entries, key, filter_label)

            if filtered_entries:
                do_export = input("Export these secrets? (y/N): ").lower().startswith("y")
                if do_export:
                    fmt = "md" if input("Format (1: Markdown Table, 2: Plain Text) [1]: ").strip() != "2" else "txt"
                    default_out = f"decodedSecrets.{fmt}"
                    out_file = input(f"Output filename [{default_out}]: ").strip() or default_out
                    out_path = vault.export_entries(filtered_entries, key, out_file, fmt)
                    print_success(f"Exported {len(filtered_entries)} secrets to {out_path.name}")

        elif choice == "2":
            key = get_master_key()
            title = input("Enter Title/Service (e.g. GitHub Token, Bank) [optional]: ").strip()
            cat = input("Enter Category (Login, API Key, Note, Cloud, General) [General]: ").strip() or "General"
            tags_raw = input("Enter Tags (comma-separated, e.g. work, api, prod) [optional]: ").strip()
            tags_list = [t.strip().lstrip("#") for t in tags_raw.split(",") if t.strip()]

            secret = input("Enter Secret to encrypt: ").strip()
            if not secret:
                print_warning("Secret was empty, cancelled.")
                continue

            entry = vault.add_secret(key, secret, title=title, tags=tags_list, category=cat)
            tags_repr = f" [#{' #'.join(entry.tags)}]" if entry.tags else ""
            print_success(f"Added secret '{entry.title or entry.secret}' to line {entry.line_number}{tags_repr}")

        elif choice == "3":
            key = get_master_key()
            print_info("Enter simple secrets line by line. Submit an empty line to finish:")
            batch_list = []
            while True:
                line = input(f"Secret #{len(batch_list) + 1}: ").strip()
                if not line:
                    break
                batch_list.append(line)
            if batch_list:
                added = vault.add_secrets_batch(key, batch_list)
                print_success(f"Batch added {len(added)} secrets under Key.")
            else:
                print_info("No secrets entered.")

        elif choice == "4":
            key = get_master_key()
            entries = vault.query_secrets(key)
            if not entries:
                print_warning("No secrets found for this key to delete.")
                continue
            display_entries_table(entries, key)
            target = input("\nEnter the '#' number of the secret to delete (or '0' to cancel): ").strip()
            try:
                t_idx = int(target)
                if 1 <= t_idx <= len(entries):
                    selected = entries[t_idx - 1]
                    name_repr = selected.title or selected.secret
                    confirm = input(f"Delete '{name_repr}' at Line {selected.line_number}? (y/N): ")
                    if confirm.lower().startswith('y'):
                        vault.delete_by_line_numbers([selected.line_number])
                        print_success(f"Deleted secret at line {selected.line_number}")
                    else:
                        print_info("Deletion cancelled.")
                elif t_idx == 0:
                    print_info("Cancelled.")
                else:
                    print_error("Invalid selection index.")
            except ValueError:
                print_error("Please enter a valid number.")

        elif choice == "5":
            new_path_str = input(f"Enter new vault file path [{vault.path}]: ").strip()
            if new_path_str:
                vault_path = Path(new_path_str).resolve()
                vault = VigenereVault(vault_path)
                print_success(f"Switched vault file to: {vault.path}")


# ==========================================
# Main Argument Parser
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Vigenère Vault: Salted Hash-Driven Multi-Key Secret Manager with Tag/Property Filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to encrypted vault file (default: Secrets.txt)",
        default=None
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # Command: list / query
    list_p = subparsers.add_parser("list", aliases=["query"], help="List / decrypt secrets with optional filters")
    list_p.add_argument("-k", "--key", help="Master key (prompts securely if omitted)")
    list_p.add_argument("-t", "--tag", help="Filter by specific tag (e.g. work, api)", default=None)
    list_p.add_argument("-c", "--category", help="Filter by category (e.g. Login, API Key)", default=None)
    list_p.add_argument("-q", "--search", help="Search text across title, secret and tags", default=None)
    list_p.add_argument("--export", help="Export matching secrets to file path", default=None)
    list_p.add_argument("--format", choices=["txt", "md"], default="md", help="Export format (default: md)")

    # Command: add
    add_p = subparsers.add_parser("add", help="Add a new secret with optional title, tags, and category")
    add_p.add_argument("-k", "--key", help="Master key (prompts securely if omitted)")
    add_p.add_argument("-s", "--secret", help="Secret text to encrypt (prompts if omitted)")
    add_p.add_argument("--title", help="Title or label for the secret", default="")
    add_p.add_argument("--tags", help="Comma-separated tags (e.g. 'work,api,prod')", default="")
    add_p.add_argument("-c", "--category", help="Category (Login, API Key, Note, General)", default="General")

    # Command: delete
    del_p = subparsers.add_parser("delete", aliases=["rm"], help="Delete a secret by matching key")
    del_p.add_argument("-k", "--key", help="Master key (prompts securely if omitted)")
    del_p.add_argument("-l", "--line", type=int, help="Specific vault line number to delete (optional)")

    # Command: create
    create_p = subparsers.add_parser("create", help="Create an empty vault file")
    create_p.add_argument("path", help="New vault file path")

    # Command: interactive
    subparsers.add_parser("interactive", help="Start interactive CLI menu")

    args = parser.parse_args()
    vault_path = resolve_vault_path(args.file)

    if not args.command or args.command == "interactive":
        interactive_menu(vault_path)
        return

    vault = VigenereVault(vault_path)

    if args.command == "create":
        new_vault = VigenereVault(args.path)
        new_vault.ensure_vault_exists()
        print_success(f"Initialized empty vault at {new_vault.path}")
        return

    if args.command in ["list", "query"]:
        key = get_master_key(args.key)
        tag_val = args.tag.lstrip("#") if args.tag else None
        entries = vault.query_secrets(
            key,
            filter_tag=tag_val,
            filter_category=args.category,
            filter_text=args.search
        )
        filter_str = f"Tag=#{tag_val}" if tag_val else ""
        if args.category:
            filter_str += f" Cat={args.category}"
        if args.search:
            filter_str += f" Search='{args.search}'"
        display_entries_table(entries, key, filter_str.strip())
        if args.export and entries:
            out = vault.export_entries(entries, key, args.export, args.format)
            print_success(f"Exported {len(entries)} secrets to {out}")

    elif args.command == "add":
        key = get_master_key(args.key)
        secret = args.secret
        if not secret:
            secret = input("Secret to encrypt: ").strip()
        if not secret:
            print_error("Cannot add an empty secret.")
            sys.exit(1)

        tags_list = [t.strip().lstrip("#") for t in args.tags.split(",") if t.strip()]
        entry = vault.add_secret(
            key,
            secret,
            title=args.title,
            tags=tags_list,
            category=args.category
        )
        tags_repr = f" [#{' #'.join(entry.tags)}]" if entry.tags else ""
        print_success(f"Added secret '{entry.title or entry.secret}' to line {entry.line_number}{tags_repr}")

    elif args.command in ["delete", "rm"]:
        key = get_master_key(args.key)
        if args.line:
            cnt = vault.delete_by_line_numbers([args.line])
            if cnt:
                print_success(f"Deleted line {args.line} from vault.")
            else:
                print_warning(f"Line {args.line} not found.")
        else:
            entries = vault.query_secrets(key)
            if not entries:
                print_warning("No matching secrets found to delete.")
                return
            display_entries_table(entries, key)
            target = input("Enter '#' number to delete: ").strip()
            try:
                idx = int(target)
                if 1 <= idx <= len(entries):
                    vault.delete_by_line_numbers([entries[idx - 1].line_number])
                    print_success(f"Deleted secret #{idx}")
                else:
                    print_error("Invalid index.")
            except ValueError:
                print_error("Invalid input.")


if __name__ == "__main__":
    main()
