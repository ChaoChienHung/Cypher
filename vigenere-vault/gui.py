#!/usr/bin/env python3
"""
Modern Graphical User Interface (GUI) for Vigenère Vault.
Built with Python's native Tkinter & TTK.
"""

from pathlib import Path
import sys

# Safe Tkinter import with friendly troubleshooting advice
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("\n[!] 錯誤：目前的 Python 環境缺少 Tkinter 模組支援。")
    print("💡 快速解決方案（任選一種）：")
    print("  1. 【推薦】使用您目前 (base) 環境的 python 直接執行：")
    print("     python vigenere-vault/gui.py")
    print("  2. 若要繼續使用 Homebrew 的 python3，請安裝 Tkinter 擴充：")
    print("     brew install python-tk@3.15")
    print("  3. 或改用 macOS 系統內建的 Python 3 執行：")
    print("     /usr/bin/python3 vigenere-vault/gui.py\n")
    sys.exit(1)
from typing import List, Optional

# Ensure core module is importable
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core import VigenereVault, VaultEntry


class VigenereVaultGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Vigenère Vault - 機密保險庫")
        self.root.geometry("820x620")
        self.root.minsize(700, 500)

        # State
        self.current_vault_path = tk.StringVar(value=self._find_default_vault())
        self.master_key = tk.StringVar()
        self.show_key_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="就緒 (Ready)")
        self.cached_entries: List[VaultEntry] = []

        self._setup_style()
        self._build_ui()
        self._update_vault_status_indicator()

    def _find_default_vault(self) -> str:
        candidates = [
            Path("Secrets.txt"),
            current_dir / "Secrets.txt",
            current_dir.parent / "Secrets.txt",
        ]
        for p in candidates:
            if p.exists():
                return str(p.resolve())
        return str((current_dir.parent / "Secrets.txt").resolve())

    def _setup_style(self):
        style = ttk.Style()
        # Use clam/default depending on OS
        if "aqua" in style.theme_names():
            style.theme_use("aqua")
        else:
            style.theme_use("clam")

        # Custom styling
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("SubHeader.TLabel", font=("Helvetica", 11), foreground="#555")
        style.configure("Accent.TButton", font=("Helvetica", 11, "bold"))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Helvetica", 10))

    def _build_ui(self):
        # Main layout frame
        main_frame = ttk.Frame(self.root, padding="14")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Top Panel: Vault File & Master Key
        top_frame = ttk.LabelFrame(main_frame, text=" 保險庫與主金鑰設定 ", padding="10")
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Vault file row
        ttk.Label(top_frame, text="保險庫檔案:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        file_entry = ttk.Entry(top_frame, textvariable=self.current_vault_path, width=48)
        file_entry.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=4)
        
        btn_box = ttk.Frame(top_frame)
        btn_box.grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(btn_box, text="瀏覽...", command=self._browse_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_box, text="新建 Vault", command=self._create_new_vault).pack(side=tk.LEFT, padx=2)

        # Master Key row
        ttk.Label(top_frame, text="解密金鑰 (Key):").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.key_entry = ttk.Entry(top_frame, textvariable=self.master_key, show="*", width=36)
        self.key_entry.grid(row=1, column=1, sticky=tk.EW, padx=4, pady=4)
        self.key_entry.bind("<Return>", lambda e: self.query_secrets())

        key_action_box = ttk.Frame(top_frame)
        key_action_box.grid(row=1, column=2, padx=4, pady=4)
        ttk.Checkbutton(
            key_action_box,
            text="顯示金鑰",
            variable=self.show_key_var,
            command=self._toggle_key_visibility
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            key_action_box,
            text="🔓 解密查詢",
            style="Accent.TButton",
            command=self.query_secrets
        ).pack(side=tk.LEFT, padx=4)

        top_frame.columnconfigure(1, weight=1)

        # 2. Notebook Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=4)

        # Tab 1: Secrets Browser & Query
        self.tab_query = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_query, text=" 🔍 機密清單 (Query) ")
        self._build_query_tab()

        # Tab 2: Add Secrets
        self.tab_add = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_add, text=" ➕ 新增機密 (Add) ")
        self._build_add_tab()

        # Tab 3: Security & Cryptography Info
        self.tab_info = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_info, text=" ℹ️ 密碼學架構 (Specs) ")
        self._build_info_tab()

        # 3. Bottom Status Bar
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(8, 3))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_status = ttk.Label(status_bar, textvariable=self.status_var, font=("Helvetica", 9))
        self.lbl_status.pack(side=tk.LEFT)

    def _build_query_tab(self):
        # Action Toolbar
        toolbar = ttk.Frame(self.tab_query)
        toolbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(toolbar, text="📋 複製選取機密", command=self._copy_selected_secret).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="📤 匯出 Markdown", command=lambda: self._export_secrets("md")).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="📄 匯出純文字檔", command=lambda: self._export_secrets("txt")).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🗑️ 刪除所選機密", command=self._delete_selected_secret).pack(side=tk.RIGHT, padx=3)

        # Treeview Table
        tree_frame = ttk.Frame(self.tab_query)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("idx", "line", "salt", "secret")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("idx", text="#", anchor=tk.CENTER)
        self.tree.heading("line", text="行號 (Line)", anchor=tk.CENTER)
        self.tree.heading("salt", text="隨機鹽值 (Salt)", anchor=tk.CENTER)
        self.tree.heading("secret", text="解密明文 (Plaintext Secret)", anchor=tk.W)

        self.tree.column("idx", width=45, minwidth=35, anchor=tk.CENTER)
        self.tree.column("line", width=90, minwidth=70, anchor=tk.CENTER)
        self.tree.column("salt", width=120, minwidth=90, anchor=tk.CENTER)
        self.tree.column("secret", width=460, minwidth=200, anchor=tk.W)

        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Double click to copy
        self.tree.bind("<Double-1>", lambda e: self._copy_selected_secret())

    def _build_add_tab(self):
        container = ttk.Frame(self.tab_add)
        container.pack(fill=tk.BOTH, expand=True)

        # Single add box
        box_single = ttk.LabelFrame(container, text=" 新增單筆機密 ", padding="10")
        box_single.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(box_single, text="機密文字:").pack(anchor=tk.W, pady=2)
        self.single_secret_entry = ttk.Entry(box_single, font=("Helvetica", 11))
        self.single_secret_entry.pack(fill=tk.X, pady=4)
        self.single_secret_entry.bind("<Return>", lambda e: self._add_single_secret())

        ttk.Button(box_single, text="➕ 加密並儲存", command=self._add_single_secret).pack(anchor=tk.E, pady=4)

        # Batch add box
        box_batch = ttk.LabelFrame(container, text=" 批次新增機密 (一行一筆) ", padding="10")
        box_batch.pack(fill=tk.BOTH, expand=True)

        self.batch_text = tk.Text(box_batch, height=8, font=("Helvetica", 10))
        self.batch_text.pack(fill=tk.BOTH, expand=True, pady=4)

        ttk.Button(box_batch, text="📥 批次加密並儲存", command=self._add_batch_secrets).pack(anchor=tk.E, pady=4)

    def _build_info_tab(self):
        info_text = tk.Text(self.tab_info, wrap=tk.WORD, font=("Courier", 10), padx=8, pady=8)
        info_text.pack(fill=tk.BOTH, expand=True)

        specs = (
            "==========================================================\n"
            "       Vigenère Vault 密碼學架構與規格摘要\n"
            "==========================================================\n\n"
            "1. 金鑰延伸 (KDF / Keystream):\n"
            "   - SHA-256(Random_Salt_8 + Key) -> 64-char Hex Keystream\n"
            "   - 每個十六進位字元 (0~15) 作為擴充維吉尼亞密碼的位移量。\n\n"
            "2. 隨機加鹽 (Salt / Nonce):\n"
            "   - 每次加密自動生成 8 位數密碼學安全隨機碼 (secrets.randbelow)。\n"
            "   - 達成語意安全 (Semantic Security)，防範彩虹表與重送比對。\n\n"
            "3. 擴充字元集 (Extended Polyalphabetic Substitution):\n"
            "   - 英文字母 (a-z, A-Z, mod 26)\n"
            "   - 33 種常見 ASCII 特殊符號與空格 (mod 33)\n\n"
            "4. 明文前綴驗證與多金鑰隔離 (Plausible Deniability):\n"
            "   - 密文封裝: Salt(8) + Encrypt(Key + Secret)\n"
            "   - 只有持有正確 Key 的使用者能解密驗證前綴，不同使用者的資料在同一個檔案內完全隔離。\n\n"
            "詳細分析請見專案 docs/technical-analysis.md。\n"
        )
        info_text.insert(tk.END, specs)
        info_text.configure(state=tk.DISABLED)

    # ----------------------------------------------------
    # Event Handlers & Core Actions
    # ----------------------------------------------------
    def _toggle_key_visibility(self):
        self.key_entry.configure(show="" if self.show_key_var.get() else "*")

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="選擇保險庫檔案",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.current_vault_path.set(path)
            self._update_vault_status_indicator()

    def _create_new_vault(self):
        path = filedialog.asksaveasfilename(
            title="新建保險庫檔案",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if path:
            vault = VigenereVault(path)
            vault.ensure_vault_exists()
            self.current_vault_path.set(path)
            self._update_vault_status_indicator()
            messagebox.showinfo("成功", f"已建立新的保險庫檔案：\n{path}")

    def _update_vault_status_indicator(self):
        p = Path(self.current_vault_path.get())
        if p.exists():
            self.status_var.set(f"已就緒 | 保險庫: {p.name} ({p.stat().st_size} bytes)")
        else:
            self.status_var.set(f"檔案不存在 (將於新增機密時自動建立): {p.name}")

    def query_secrets(self):
        key = self.master_key.get()
        if not key:
            messagebox.showwarning("提示", "請先輸入解密金鑰 (Key)！")
            self.key_entry.focus_set()
            return

        vault = VigenereVault(self.current_vault_path.get())
        if not vault.exists():
            messagebox.showinfo("提示", f"保險庫檔案尚未存在：\n{vault.path}")
            return

        self.cached_entries = vault.query_secrets(key)

        # Clear existing items in tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, entry in enumerate(self.cached_entries, start=1):
            self.tree.insert("", tk.END, iid=str(idx), values=(
                idx,
                f"L{entry.line_number}",
                entry.salt,
                entry.secret
            ))

        self.notebook.select(self.tab_query)
        count = len(self.cached_entries)
        if count > 0:
            self.status_var.set(f"查詢完成：成功解密 {count} 筆機密。")
        else:
            self.status_var.set("查詢完成：此檔案中未找到符合此金鑰的機密。")
            messagebox.showinfo("查詢結果", "未找到符合此金鑰的機密。\n（可能金鑰錯誤，或該機密屬於其他金鑰）")

    def _copy_selected_secret(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "請先在列表中選取一筆機密！")
            return
        item_id = selected[0]
        secret_val = self.tree.item(item_id, "values")[3]

        self.root.clipboard_clear()
        self.root.clipboard_append(secret_val)
        self.status_var.set("已將機密複製到系統剪貼簿！")
        messagebox.showinfo("複製成功", "已將機密複製到剪貼簿！")

    def _export_secrets(self, fmt: str):
        if not self.cached_entries:
            messagebox.showwarning("提示", "目前沒有已解密的機密可供匯出，請先執行查詢！")
            return

        ext = f".{fmt}"
        filename = f"decodedSecrets{ext}"
        save_path = filedialog.asksaveasfilename(
            title=f"匯出為 {fmt.upper()} 檔案",
            initialfile=filename,
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} file", f"*{ext}")]
        )
        if save_path:
            vault = VigenereVault(self.current_vault_path.get())
            out_p = vault.export_entries(self.cached_entries, self.master_key.get(), save_path, fmt)
            messagebox.showinfo("匯出成功", f"已成功匯出 {len(self.cached_entries)} 筆機密至：\n{out_p}")
            self.status_var.set(f"匯出成功: {out_p.name}")

    def _delete_selected_secret(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "請先在列表中選取要刪除的機密！")
            return

        item_id = selected[0]
        idx = int(self.tree.item(item_id, "values")[0])
        entry = self.cached_entries[idx - 1]

        confirm = messagebox.askyesno(
            "確認刪除",
            f"確定要從保險庫中刪除以下機密嗎？\n\n行號: L{entry.line_number}\n內容: {entry.secret}\n\n此動作無法復原！"
        )
        if confirm:
            vault = VigenereVault(self.current_vault_path.get())
            vault.delete_by_line_numbers([entry.line_number])
            messagebox.showinfo("成功", "該機密已自保險庫中刪除。")
            self.query_secrets()

    def _add_single_secret(self):
        key = self.master_key.get()
        if not key:
            messagebox.showwarning("提示", "請先在上方輸入主金鑰 (Key)！")
            self.key_entry.focus_set()
            return

        secret = self.single_secret_entry.get().strip()
        if not secret:
            messagebox.showwarning("提示", "請輸入機密文字！")
            return

        vault = VigenereVault(self.current_vault_path.get())
        entry = vault.add_secret(key, secret)
        self.single_secret_entry.delete(0, tk.END)
        self._update_vault_status_indicator()
        messagebox.showinfo("新增成功", f"機密已成功加密寫入！\n行號: L{entry.line_number}\nSalt: {entry.salt}")
        self.query_secrets()

    def _add_batch_secrets(self):
        key = self.master_key.get()
        if not key:
            messagebox.showwarning("提示", "請先在上方輸入主金鑰 (Key)！")
            self.key_entry.focus_set()
            return

        text = self.batch_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "批次輸入框內無文字！")
            return

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        vault = VigenereVault(self.current_vault_path.get())
        added = vault.add_secrets_batch(key, lines)
        self.batch_text.delete("1.0", tk.END)
        self._update_vault_status_indicator()
        messagebox.showinfo("批次新增成功", f"已成功加密並新增 {len(added)} 筆機密！")
        self.query_secrets()


def main():
    root = tk.Tk()
    app = VigenereVaultGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
