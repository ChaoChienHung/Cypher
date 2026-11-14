#!/usr/bin/env python3
"""
Modern PySide6 GUI for Vigenère Vault.
Features a dark cybersecurity aesthetic, real-time search filtering,
clipboard integration, batch encryption, and multi-format exports.
"""

from pathlib import Path
import sys
from typing import List, Optional

# Ensure core module is importable
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core import VigenereVault, VaultEntry

try:
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QFont, QIcon, QAction, QColor, QPalette, QKeySequence, QShortcut
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
        QHeaderView, QTabWidget, QTextEdit, QMessageBox, QFileDialog,
        QStatusBar, QFrame, QSplitter, QCheckBox, QAbstractItemView
    )
except ImportError:
    print("\n[!] 錯誤：未找到 PySide6 模組。")
    print("💡 請在終端機中執行：")
    print("   pip install PySide6")
    print("   或：python -m pip install PySide6\n")
    sys.exit(1)


# Dark Glass / Cyber-Security Style Sheet (QSS)
MODERN_DARK_QSS = """
QMainWindow {
    background-color: #121318;
}
QWidget {
    background-color: #121318;
    color: #E2E8F0;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
}
QFrame.CardFrame {
    background-color: #1A1C23;
    border: 1px solid #2D3139;
    border-radius: 10px;
    padding: 12px;
}
QLabel {
    background-color: transparent;
    color: #CBD5E1;
}
QLabel.TitleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #38BDF8;
}
QLabel.SubtitleLabel {
    font-size: 11px;
    color: #64748B;
}
QLineEdit, QTextEdit {
    background-color: #0F1015;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    color: #F8FAFC;
    selection-background-color: #0284C7;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #38BDF8;
    background-color: #141720;
}
QPushButton {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    color: #F1F5F9;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}
QPushButton:pressed {
    background-color: #0F172A;
}
QPushButton.PrimaryBtn {
    background-color: #0284C7;
    border: 1px solid #0369A1;
    color: #FFFFFF;
    font-weight: bold;
}
QPushButton.PrimaryBtn:hover {
    background-color: #0EA5E9;
    border-color: #38BDF8;
}
QPushButton.DangerBtn {
    background-color: #881337;
    border: 1px solid #9F1239;
    color: #FFE4E6;
}
QPushButton.DangerBtn:hover {
    background-color: #9F1239;
}
QTabWidget::pane {
    border: 1px solid #2D3139;
    background-color: #1A1C23;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background-color: #121318;
    color: #94A3B8;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid transparent;
}
QTabBar::tab:selected {
    background-color: #1A1C23;
    color: #38BDF8;
    border: 1px solid #2D3139;
    border-bottom: 1px solid #1A1C23;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #1A1C23;
    color: #E2E8F0;
}
QTableWidget {
    background-color: #0F1015;
    border: 1px solid #2D3139;
    border-radius: 6px;
    gridline-color: #1E222B;
    color: #F1F5F9;
    selection-background-color: #0369A1;
    selection-color: #FFFFFF;
}
QHeaderView::section {
    background-color: #1A1C23;
    color: #94A3B8;
    font-weight: bold;
    padding: 6px;
    border: none;
    border-bottom: 2px solid #2D3139;
}
QScrollBar:vertical {
    border: none;
    background: #121318;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QStatusBar {
    background-color: #0F1015;
    color: #94A3B8;
    border-top: 1px solid #1E222B;
}
"""


class VigenereVaultPySide(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vigenère Vault 2.0 - 密碼學機密保險庫")
        self.resize(920, 680)
        self.setMinimumSize(780, 520)

        # State
        self.cached_entries: List[VaultEntry] = []
        self.filtered_entries: List[VaultEntry] = []
        self.default_vault_path = self._locate_default_vault()

        self._init_ui()
        self.setStyleSheet(MODERN_DARK_QSS)
        self._update_vault_file_status()

    def _locate_default_vault(self) -> Path:
        candidates = [
            Path("Secrets.txt"),
            current_dir / "Secrets.txt",
            current_dir.parent / "Secrets.txt",
        ]
        for p in candidates:
            if p.exists():
                return p.resolve()
        return (current_dir.parent / "Secrets.txt").resolve()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 12)
        main_layout.setSpacing(12)

        # Top Control Card (Vault path & Key)
        top_card = QFrame()
        top_card.setProperty("class", "CardFrame")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(12, 12, 12, 12)
        top_layout.setSpacing(8)

        # Row 1: Header title
        title_box = QHBoxLayout()
        title_lbl = QLabel("🔐 Vigenère Vault")
        title_lbl.setProperty("class", "TitleLabel")
        subtitle_lbl = QLabel("SHA-256 Nonce-Salted Multi-Tenant Key Vault")
        subtitle_lbl.setProperty("class", "SubtitleLabel")
        title_box.addWidget(title_lbl)
        title_box.addWidget(subtitle_lbl)
        title_box.addStretch()
        top_layout.addLayout(title_box)

        # Row 2: File Selector
        file_row = QHBoxLayout()
        file_lbl = QLabel("保險庫檔案:")
        file_lbl.setFixedWidth(80)
        self.file_input = QLineEdit(str(self.default_vault_path))
        self.file_input.textChanged.connect(self._update_vault_file_status)

        browse_btn = QPushButton("瀏覽檔案...")
        browse_btn.clicked.connect(self._browse_vault_file)
        new_vault_btn = QPushButton("新建 Vault")
        new_vault_btn.clicked.connect(self._create_new_vault)

        file_row.addWidget(file_lbl)
        file_row.addWidget(self.file_input)
        file_row.addWidget(browse_btn)
        file_row.addWidget(new_vault_btn)
        top_layout.addLayout(file_row)

        # Row 3: Master Key Input
        key_row = QHBoxLayout()
        key_lbl = QLabel("主解密金鑰:")
        key_lbl.setFixedWidth(80)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("請輸入對應此機密的 Master Key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.returnPressed.connect(self.query_secrets)

        self.show_key_check = QCheckBox("顯示金鑰")
        self.show_key_check.toggled.connect(self._toggle_key_visibility)

        self.unlock_btn = QPushButton("🔓 解密查詢 (Unlock)")
        self.unlock_btn.setProperty("class", "PrimaryBtn")
        self.unlock_btn.clicked.connect(self.query_secrets)

        key_row.addWidget(key_lbl)
        key_row.addWidget(self.key_input)
        key_row.addWidget(self.show_key_check)
        key_row.addWidget(self.unlock_btn)
        top_layout.addLayout(key_row)

        main_layout.addWidget(top_card)

        # Main Notebook Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch=1)

        # Tab 1: Secrets Query & Management
        self.tab_query = QWidget()
        self._init_query_tab()
        self.tabs.addTab(self.tab_query, " 🔍 機密清單 (Secrets Vault) ")

        # Tab 2: Add Secrets
        self.tab_add = QWidget()
        self._init_add_tab()
        self.tabs.addTab(self.tab_add, " ➕ 新增機密 (Add Secret) ")

        # Tab 3: Technical Docs & Mindset
        self.tab_docs = QWidget()
        self._init_docs_tab()
        self.tabs.addTab(self.tab_docs, " ℹ️ 密碼學技術與思維 (Architecture) ")

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就緒 (Ready)")

    def _init_query_tab(self):
        layout = QVBoxLayout(self.tab_query)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search / Filter Bar + Action Buttons
        toolbar = QHBoxLayout()
        search_lbl = QLabel("即時搜尋:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入關鍵字過濾已解密的明文...")
        self.search_input.textChanged.connect(self._filter_secrets)

        self.copy_btn = QPushButton("📋 複製選取機密")
        self.copy_btn.clicked.connect(self._copy_selected_secret)

        self.export_md_btn = QPushButton("📤 匯出 Markdown")
        self.export_md_btn.clicked.connect(lambda: self._export_secrets("md"))

        self.export_txt_btn = QPushButton("📄 匯出 TXT")
        self.export_txt_btn.clicked.connect(lambda: self._export_secrets("txt"))

        self.delete_btn = QPushButton("🗑️ 刪除選取")
        self.delete_btn.setProperty("class", "DangerBtn")
        self.delete_btn.clicked.connect(self._delete_selected_secret)

        toolbar.addWidget(search_lbl)
        toolbar.addWidget(self.search_input, stretch=1)
        toolbar.addWidget(self.copy_btn)
        toolbar.addWidget(self.export_md_btn)
        toolbar.addWidget(self.export_txt_btn)
        toolbar.addWidget(self.delete_btn)
        layout.addLayout(toolbar)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "保險庫行號", "隨機鹽值 (Salt)", "解密明文 (Plaintext)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._copy_selected_secret)
        layout.addWidget(self.table)

    def _init_add_tab(self):
        layout = QVBoxLayout(self.tab_add)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Single Add Box
        single_frame = QFrame()
        single_frame.setProperty("class", "CardFrame")
        s_layout = QVBoxLayout(single_frame)
        s_layout.addWidget(QLabel("<b>單筆機密加密寫入:</b>"))

        s_input_row = QHBoxLayout()
        self.single_input = QLineEdit()
        self.single_input.setPlaceholderText("請輸入要加密存放的密碼、Token 或機密文字...")
        self.single_input.returnPressed.connect(self._add_single_secret)

        s_add_btn = QPushButton("➕ 加密寫入")
        s_add_btn.setProperty("class", "PrimaryBtn")
        s_add_btn.clicked.connect(self._add_single_secret)

        s_input_row.addWidget(self.single_input, stretch=1)
        s_input_row.addWidget(s_add_btn)
        s_layout.addLayout(s_input_row)
        layout.addWidget(single_frame)

        # Batch Add Box
        batch_frame = QFrame()
        batch_frame.setProperty("class", "CardFrame")
        b_layout = QVBoxLayout(batch_frame)
        b_layout.addWidget(QLabel("<b>批次機密寫入 (一行一筆):</b>"))

        self.batch_text = QTextEdit()
        self.batch_text.setPlaceholderText("可直接貼上多行文字，每一行將會自動分配獨立的 8 位數 Salt 並加密...")
        b_layout.addWidget(self.batch_text)

        b_btn_row = QHBoxLayout()
        b_btn_row.addStretch()
        b_add_btn = QPushButton("📥 批次加密全部寫入")
        b_add_btn.setProperty("class", "PrimaryBtn")
        b_add_btn.clicked.connect(self._add_batch_secrets)
        b_btn_row.addWidget(b_add_btn)
        b_layout.addLayout(b_btn_row)

        layout.addWidget(batch_frame, stretch=1)

    def _init_docs_tab(self):
        layout = QVBoxLayout(self.tab_docs)
        layout.setContentsMargins(12, 12, 12, 12)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Menlo", 12))

        doc_content = (
            "========================================================================\n"
            "                 Vigenère Vault 密碼學技術與心態演進規格\n"
            "========================================================================\n\n"
            "一、核心技術與演算法 (Core Primitives)\n"
            "------------------------------------------------------------------------\n"
            "1. 隨機加鹽 (8-digit Salt / Nonce):\n"
            "   每次加密皆由 secrets.randbelow() 生成 8 位數隨機數字 (10000000..99999999)。\n"
            "   達成語意安全 (Semantic Security)，防範彩虹表與重送比對。\n\n"
            "2. SHA-256 偽隨機流位移 (Hash-based Keystream Generation):\n"
            "   以 SHA256(Salt + Key) 展開成 64 字元的十六進位串流，作為維吉尼亞密碼的動態位移量。\n\n"
            "3. 擴充字元集 (Extended Polyalphabetic Substitution):\n"
            "   支援大小寫英文字母 (mod 26) 與 33 種常見 ASCII 特殊符號 (mod 33)。\n\n"
            "4. 明文前綴驗證與多金鑰隔離 (Plausible Deniability):\n"
            "   密文格式: Salt(8) + Encrypt(Key + Secret)。\n"
            "   解密時只有 Key 符合者能解出並通過前綴檢驗，不同金鑰的機密在同個檔案內互不干擾、\n"
            "   且外界無法探知檔案內究竟包含多少組金鑰。\n\n"
            "二、四步演化心智模型 (The 4-Step Evolutionary Mindset)\n"
            "------------------------------------------------------------------------\n"
            "  [基礎代換]   維吉尼亞/凱撒加密法。\n"
            "      ↓\n"
            "  [克服週期]   使用 SHA-256 展開非循環金鑰流。\n"
            "      ↓\n"
            "  [語意安全]   引入 8-digit Salt 防彩虹表。\n"
            "      ↓\n"
            "  [身分隔離]   前綴 Key 比對驗證，實現單檔多 Key 可抵賴隔離。\n\n"
            "詳細技術文件請閱讀: docs/technical-analysis.md 與 docs/gui-architecture.md。\n"
        )
        text_edit.setText(doc_content)
        layout.addWidget(text_edit)

    # ------------------------------------------------------------------
    # Actions & Event Handlers
    # ------------------------------------------------------------------
    def _toggle_key_visibility(self, checked: bool):
        self.key_input.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)

    def _browse_vault_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇保險庫檔案", str(self.default_vault_path.parent), "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.file_input.setText(file_path)
            self._update_vault_file_status()

    def _create_new_vault(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "新建保險庫檔案", "Secrets.txt", "Text Files (*.txt)"
        )
        if file_path:
            vault = VigenereVault(file_path)
            vault.ensure_vault_exists()
            self.file_input.setText(file_path)
            self._update_vault_file_status()
            QMessageBox.information(self, "成功", f"已建立新的空白保險庫：\n{file_path}")

    def _update_vault_file_status(self):
        p = Path(self.file_input.text().strip())
        if p.exists() and p.is_file():
            size = p.stat().st_size
            self.status_bar.showMessage(f"保險庫檔案已載入: {p.name} ({size} bytes)")
        else:
            self.status_bar.showMessage(f"檔案不存在 (將於寫入時自動建立): {p.name}")

    def query_secrets(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "警告", "請先輸入解密金鑰 (Master Key)！")
            self.key_input.setFocus()
            return

        vault_path = self.file_input.text().strip()
        vault = VigenereVault(vault_path)
        if not vault.exists():
            QMessageBox.information(self, "提示", f"保險庫檔案尚未存在：\n{vault.path}")
            return

        self.cached_entries = vault.query_secrets(key)
        self.search_input.clear()
        self._render_table(self.cached_entries)
        self.tabs.setCurrentIndex(0)

        count = len(self.cached_entries)
        if count > 0:
            self.status_bar.showMessage(f"解密成功！找到 {count} 筆符合金鑰的機密。")
        else:
            self.status_bar.showMessage("解密完成：未找到符合此金鑰的機密。")
            QMessageBox.information(
                self, "查詢結果", "未找到符合此金鑰的機密。\n（可能金鑰錯誤，或該機密屬於其他金鑰隔離）"
            )

    def _render_table(self, entries: List[VaultEntry]):
        self.filtered_entries = entries
        self.table.setRowCount(len(entries))
        for row_idx, entry in enumerate(entries):
            # Column 0: Index
            item_idx = QTableWidgetItem(str(row_idx + 1))
            item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item_idx)

            # Column 1: Line number
            item_line = QTableWidgetItem(f"L{entry.line_number}")
            item_line.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, item_line)

            # Column 2: Salt
            item_salt = QTableWidgetItem(entry.salt)
            item_salt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, item_salt)

            # Column 3: Secret plaintext
            item_secret = QTableWidgetItem(entry.secret)
            item_secret.setFont(QFont("Menlo", 12))
            self.table.setItem(row_idx, 3, item_secret)

    def _filter_secrets(self, text: str):
        query = text.strip().lower()
        if not query:
            self._render_table(self.cached_entries)
            return

        matched = [e for e in self.cached_entries if query in e.secret.lower()]
        self._render_table(matched)
        self.status_bar.showMessage(f"搜尋過濾：共 {len(matched)} / {len(self.cached_entries)} 筆符合。")

    def _copy_selected_secret(self):
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_entries):
            QMessageBox.warning(self, "提示", "請先在列表中選取一筆機密！")
            return

        secret_text = self.filtered_entries[current_row].secret
        clipboard = QApplication.clipboard()
        clipboard.setText(secret_text)
        self.status_bar.showMessage(f"已複製機密至剪貼簿！")
        QMessageBox.information(self, "複製成功", "已將機密複製到系統剪貼簿！")

    def _export_secrets(self, fmt: str):
        if not self.cached_entries:
            QMessageBox.warning(self, "提示", "目前沒有已解密的機密可供匯出，請先執行解密查詢！")
            return

        ext = f".{fmt}"
        save_path, _ = QFileDialog.getSaveFileName(
            self, f"匯出為 {fmt.upper()}", f"decodedSecrets{ext}", f"{fmt.upper()} Files (*{ext})"
        )
        if save_path:
            vault = VigenereVault(self.file_input.text().strip())
            out_p = vault.export_entries(self.cached_entries, self.key_input.text().strip(), save_path, fmt)
            QMessageBox.information(self, "匯出成功", f"已成功匯出 {len(self.cached_entries)} 筆機密至：\n{out_p}")
            self.status_bar.showMessage(f"匯出完成: {out_p.name}")

    def _delete_selected_secret(self):
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_entries):
            QMessageBox.warning(self, "提示", "請先在列表中選取要刪除的機密！")
            return

        entry = self.filtered_entries[current_row]
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要自保險庫中永久刪除此機密嗎？\n\n行號: L{entry.line_number}\n內容: {entry.secret}\n\n此動作無法還原！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            vault = VigenereVault(self.file_input.text().strip())
            vault.delete_by_line_numbers([entry.line_number])
            QMessageBox.information(self, "成功", "該機密已自保險庫中刪除！")
            self.query_secrets()

    def _add_single_secret(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "警告", "請先在上方輸入主金鑰 (Key)！")
            self.key_input.setFocus()
            return

        secret = self.single_input.text().strip()
        if not secret:
            QMessageBox.warning(self, "警告", "請輸入機密文字！")
            return

        vault = VigenereVault(self.file_input.text().strip())
        entry = vault.add_secret(key, secret)
        self.single_input.clear()
        self._update_vault_file_status()
        QMessageBox.information(
            self, "新增成功", f"機密已成功加密寫入！\n行號: L{entry.line_number}\nSalt: {entry.salt}"
        )
        self.query_secrets()

    def _add_batch_secrets(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "警告", "請先在上方輸入主金鑰 (Key)！")
            self.key_input.setFocus()
            return

        text = self.batch_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "批次輸入框內無文字！")
            return

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        vault = VigenereVault(self.file_input.text().strip())
        added = vault.add_secrets_batch(key, lines)
        self.batch_text.clear()
        self._update_vault_file_status()
        QMessageBox.information(self, "批次新增成功", f"已成功加密並新增 {len(added)} 筆機密！")
        self.query_secrets()


def main():
    app = QApplication(sys.argv)
    window = VigenereVaultPySide()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
