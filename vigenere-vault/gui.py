#!/usr/bin/env python3
"""
Modern PySide6 GUI for Vigenère Vault.
Features a dark cybersecurity aesthetic, structured properties (Title, Category, Tags),
multi-criteria dynamic filtering, real-time search, and clipboard integration.
"""

from pathlib import Path
import sys
from typing import List, Optional, Set

# Ensure core module is importable
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core import VigenereVault, VaultEntry

try:
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QFont, QIcon, QAction, QColor, QPalette, QKeySequence
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
        QHeaderView, QTabWidget, QTextEdit, QMessageBox, QFileDialog,
        QStatusBar, QFrame, QSplitter, QCheckBox, QAbstractItemView,
        QComboBox
    )
except ImportError:
    print("\n[!] 錯誤：未找到 PySide6 模組。")
    print("💡 請在終端機中執行：")
    print("   pip install PySide6\n")
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
QLineEdit, QTextEdit, QComboBox {
    background-color: #0F1015;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    color: #F8FAFC;
    selection-background-color: #0284C7;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #38BDF8;
    background-color: #141720;
}
QComboBox QAbstractItemView {
    background-color: #1A1C23;
    border: 1px solid #334155;
    selection-background-color: #0284C7;
    color: #F8FAFC;
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
        self.setWindowTitle("Vigenère Vault 2.0 - 結構化密碼學機密保險庫")
        self.resize(1000, 700)
        self.setMinimumSize(800, 540)

        # State
        self.cached_entries: List[VaultEntry] = []
        self.filtered_entries: List[VaultEntry] = []
        self.default_vault_path = self._locate_default_vault()

        self._init_ui()
        self.setStyleSheet(MODERN_DARK_QSS)
        self._update_vault_file_status()

    def _locate_default_vault(self) -> Path:
        if getattr(sys, 'frozen', False):
            candidates = [
                Path.cwd() / "Secrets.txt",
                Path.home() / "Desktop" / "Secrets.txt",
                Path.home() / "Documents" / "Secrets.txt",
            ]
            for p in candidates:
                if p.exists():
                    return p.resolve()
            return (Path.home() / "Desktop" / "Secrets.txt").resolve()

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
        subtitle_lbl = QLabel("Multi-Tenant Key Vault with Property & Tag Filtering")
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
        self.key_input.setPlaceholderText("請輸入解鎖此機密的 Master Key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.returnPressed.connect(self.query_secrets)

        self.show_key_check = QCheckBox("顯示金鑰")
        self.show_key_check.toggled.connect(self._toggle_key_visibility)

        self.unlock_btn = QPushButton("🔓 解密載入 (Unlock)")
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

        # Tab 1: Secrets Query & Management (with Properties & Filter)
        self.tab_query = QWidget()
        self._init_query_tab()
        self.tabs.addTab(self.tab_query, " 🔍 機密清單與過濾 (Vault Browser) ")

        # Tab 2: Add Secrets (with Title, Category, Tags)
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

        # Multi-Criteria Filter Bar
        filter_card = QFrame()
        filter_card.setProperty("class", "CardFrame")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(8, 8, 8, 8)
        filter_layout.setSpacing(8)

        # Keyword search
        filter_layout.addWidget(QLabel("🔍 搜尋:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋標題、機密、標籤...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, stretch=2)

        # Category Filter Combobox
        filter_layout.addWidget(QLabel("📂 類型:"))
        self.cat_filter_combo = QComboBox()
        self.cat_filter_combo.addItem("全部類型 (All)")
        self.cat_filter_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.cat_filter_combo, stretch=1)

        # Tag Filter Combobox
        filter_layout.addWidget(QLabel("🏷️ 標籤:"))
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("全部標籤 (All)")
        self.tag_filter_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.tag_filter_combo, stretch=1)

        # Reset button
        reset_btn = QPushButton("重設過濾")
        reset_btn.clicked.connect(self._reset_filters)
        filter_layout.addWidget(reset_btn)

        layout.addWidget(filter_card)

        # Action Toolbar
        toolbar = QHBoxLayout()
        self.copy_btn = QPushButton("📋 複製機密")
        self.copy_btn.clicked.connect(self._copy_selected_secret)

        self.export_md_btn = QPushButton("📤 匯出 Markdown")
        self.export_md_btn.clicked.connect(lambda: self._export_secrets("md"))

        self.export_txt_btn = QPushButton("📄 匯出 TXT")
        self.export_txt_btn.clicked.connect(lambda: self._export_secrets("txt"))

        self.delete_btn = QPushButton("🗑️ 刪除所選")
        self.delete_btn.setProperty("class", "DangerBtn")
        self.delete_btn.clicked.connect(self._delete_selected_secret)

        toolbar.addWidget(self.copy_btn)
        toolbar.addWidget(self.export_md_btn)
        toolbar.addWidget(self.export_txt_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.delete_btn)
        layout.addLayout(toolbar)

        # Table Widget (Expanded with Title, Category, Tags, Timestamp)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "#", "標題 (Title)", "類型 (Category)", "標籤 (Tags)", "解密機密 (Secret)", "建立時間", "行號"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._copy_selected_secret)
        layout.addWidget(self.table)

    def _init_add_tab(self):
        layout = QVBoxLayout(self.tab_add)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Structured Add Box
        form_frame = QFrame()
        form_frame.setProperty("class", "CardFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(8)

        form_layout.addWidget(QLabel("<b>新增結構化機密 (Structured Secret Item):</b>"))

        # Row 1: Title & Category
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("標題/服務名:"))
        self.add_title_input = QLineEdit()
        self.add_title_input.setPlaceholderText("例如: GitHub Work Token、AWS S3、Netflix...")
        r1.addWidget(self.add_title_input, stretch=2)

        r1.addWidget(QLabel("類型 (Category):"))
        self.add_cat_combo = QComboBox()
        self.add_cat_combo.setEditable(True)
        self.add_cat_combo.addItems(["General", "Login", "API Key", "Token", "Cloud", "Finance", "Note", "Server"])
        r1.addWidget(self.add_cat_combo, stretch=1)
        form_layout.addLayout(r1)

        # Row 2: Tags
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("標籤 (Tags):"))
        self.add_tags_input = QLineEdit()
        self.add_tags_input.setPlaceholderText("多個標籤以逗號分隔，例如: work, api, github, prod")
        r2.addWidget(self.add_tags_input)
        form_layout.addLayout(r2)

        # Row 3: Secret Content
        r3 = QVBoxLayout()
        r3.addWidget(QLabel("機密內容 (Secret Text):"))
        self.add_secret_input = QLineEdit()
        self.add_secret_input.setPlaceholderText("請輸入要加密存放的機密文字、密碼或金鑰...")
        self.add_secret_input.returnPressed.connect(self._add_structured_secret)
        r3.addWidget(self.add_secret_input)
        form_layout.addLayout(r3)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton("➕ 加密儲存")
        add_btn.setProperty("class", "PrimaryBtn")
        add_btn.clicked.connect(self._add_structured_secret)
        btn_row.addWidget(add_btn)
        form_layout.addLayout(btn_row)

        layout.addWidget(form_frame)

        # Batch Add Box (Simple plain text import)
        batch_frame = QFrame()
        batch_frame.setProperty("class", "CardFrame")
        b_layout = QVBoxLayout(batch_frame)
        b_layout.addWidget(QLabel("<b>快速批次匯入 (一行一筆，自動加鹽):</b>"))

        self.batch_text = QTextEdit()
        self.batch_text.setPlaceholderText("可直接貼上多行文字，每一行將會自動分配獨立的 8 位數 Salt 加密...")
        b_layout.addWidget(self.batch_text)

        b_btn_row = QHBoxLayout()
        b_btn_row.addStretch()
        b_add_btn = QPushButton("📥 批次加密全部寫入")
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
            "                 Vigenère Vault 結構化機密與屬性規格\n"
            "========================================================================\n\n"
            "一、結構化機密規格 (Structured Properties)\n"
            "------------------------------------------------------------------------\n"
            "每一筆機密均被封裝為結構化物件並以維吉尼亞金鑰流全欄位加密：\n"
            "  - Title:      機密標題 / 服務名稱 (如: GitHub Token)\n"
            "  - Category:   類型分類 (如: API Key, Login, Note, Cloud)\n"
            "  - Tags:       多維度標籤清單 (如: ['work', 'prod', 'api'])\n"
            "  - Secret:     實際核心機密文字\n"
            "  - Created At: 建立時間戳記 (ISO 8601 / 本地時間)\n\n"
            "二、100% 向後相容保證 (Downward Compatibility)\n"
            "------------------------------------------------------------------------\n"
            "解密時引擎會自動偵測解密出的明文結構：\n"
            "  1. 若為標準 JSON 物件 -> 自動解析標題、標籤與類型。\n"
            "  2. 若為一般純文字 (舊版本加密的資料) -> 自動兼容載入為普通機密，\n"
            "     舊檔案無須執行任何遷移即可完美讀取。\n\n"
            "三、多維度即時過濾 (Multi-Criteria Filtering)\n"
            "------------------------------------------------------------------------\n"
            "  - 關鍵字即時比對: 同步檢索標題、標籤、類型與機密字串。\n"
            "  - 標籤下拉篩選: 動態收集當前金鑰解密出的所有唯一標籤 (Unique Tags)。\n"
            "  - 類型下拉篩選: 快速過濾 Login、API Key、Cloud 等分類。\n"
        )
        text_edit.setText(doc_content)
        layout.addWidget(text_edit)

    # ------------------------------------------------------------------
    # Actions & Filter Handlers
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
        self._refresh_filter_options()
        self._apply_filters()
        self.tabs.setCurrentIndex(0)

        count = len(self.cached_entries)
        if count > 0:
            self.status_bar.showMessage(f"解密成功！找到 {count} 筆符合金鑰的機密。")
        else:
            self.status_bar.showMessage("解密完成：未找到符合此金鑰的機密。")
            QMessageBox.information(
                self, "查詢結果", "未找到符合此金鑰的機密。\n（可能金鑰錯誤，或該機密屬於其他金鑰隔離）"
            )

    def _refresh_filter_options(self):
        """Populate the tag and category dropdowns based on decrypted entries."""
        vault = VigenereVault(self.file_input.text().strip())
        tags = vault.get_all_tags(self.cached_entries)
        cats = vault.get_all_categories(self.cached_entries)

        # Update Tag Filter
        current_tag = self.tag_filter_combo.currentText()
        self.tag_filter_combo.blockSignals(True)
        self.tag_filter_combo.clear()
        self.tag_filter_combo.addItem("全部標籤 (All)")
        for t in tags:
            self.tag_filter_combo.addItem(f"#{t}")
        # Restore selection if possible
        idx = self.tag_filter_combo.findText(current_tag)
        if idx >= 0:
            self.tag_filter_combo.setCurrentIndex(idx)
        self.tag_filter_combo.blockSignals(False)

        # Update Category Filter
        current_cat = self.cat_filter_combo.currentText()
        self.cat_filter_combo.blockSignals(True)
        self.cat_filter_combo.clear()
        self.cat_filter_combo.addItem("全部類型 (All)")
        for c in cats:
            self.cat_filter_combo.addItem(c)
        idx = self.cat_filter_combo.findText(current_cat)
        if idx >= 0:
            self.cat_filter_combo.setCurrentIndex(idx)
        self.cat_filter_combo.blockSignals(False)

    def _reset_filters(self):
        self.search_input.clear()
        self.tag_filter_combo.setCurrentIndex(0)
        self.cat_filter_combo.setCurrentIndex(0)
        self._apply_filters()

    def _apply_filters(self):
        query = self.search_input.text().strip()
        selected_tag_raw = self.tag_filter_combo.currentText()
        selected_tag = selected_tag_raw.lstrip("#") if selected_tag_raw != "全部標籤 (All)" else None

        selected_cat_raw = self.cat_filter_combo.currentText()
        selected_cat = selected_cat_raw if selected_cat_raw != "全部類型 (All)" else None

        matched = [
            e for e in self.cached_entries
            if e.matches_filter(tag=selected_tag, category=selected_cat, search_query=query)
        ]
        self._render_table(matched)

        # Update status
        filter_desc = []
        if selected_tag:
            filter_desc.append(f"標籤=#{selected_tag}")
        if selected_cat:
            filter_desc.append(f"類型={selected_cat}")
        if query:
            filter_desc.append(f"搜尋='{query}'")

        filter_info = f" (過濾條件: {', '.join(filter_desc)})" if filter_desc else ""
        self.status_bar.showMessage(f"顯示 {len(matched)} / {len(self.cached_entries)} 筆機密{filter_info}")

    def _render_table(self, entries: List[VaultEntry]):
        self.filtered_entries = entries
        self.table.setRowCount(len(entries))
        for row_idx, entry in enumerate(entries):
            # 0: Index
            item_idx = QTableWidgetItem(str(row_idx + 1))
            item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item_idx)

            # 1: Title
            title_text = entry.title or "(無標題)"
            item_title = QTableWidgetItem(title_text)
            item_title.setFont(QFont("Helvetica Neue", 12, QFont.Weight.Bold))
            self.table.setItem(row_idx, 1, item_title)

            # 2: Category
            item_cat = QTableWidgetItem(entry.category)
            item_cat.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_cat.setForeground(QColor("#FBBF24"))  # Warm yellow
            self.table.setItem(row_idx, 2, item_cat)

            # 3: Tags
            tags_text = " ".join([f"#{t}" for t in entry.tags]) if entry.tags else "-"
            item_tags = QTableWidgetItem(tags_text)
            item_tags.setForeground(QColor("#38BDF8"))  # Cyan
            self.table.setItem(row_idx, 3, item_tags)

            # 4: Secret Plaintext
            item_secret = QTableWidgetItem(entry.secret)
            item_secret.setFont(QFont("Menlo", 12))
            item_secret.setForeground(QColor("#4ADE80"))  # Green
            self.table.setItem(row_idx, 4, item_secret)

            # 5: Created Timestamp
            item_ts = QTableWidgetItem(entry.created_at or "-")
            item_ts.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_ts.setForeground(QColor("#94A3B8"))
            self.table.setItem(row_idx, 5, item_ts)

            # 6: Line number
            item_line = QTableWidgetItem(f"L{entry.line_number}")
            item_line.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_line.setForeground(QColor("#64748B"))
            self.table.setItem(row_idx, 6, item_line)

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
        if not self.filtered_entries:
            QMessageBox.warning(self, "提示", "目前沒有已篩選/解密的機密可供匯出，請先執行解密查詢！")
            return

        ext = f".{fmt}"
        save_path, _ = QFileDialog.getSaveFileName(
            self, f"匯出為 {fmt.upper()}", f"decodedSecrets{ext}", f"{fmt.upper()} Files (*{ext})"
        )
        if save_path:
            vault = VigenereVault(self.file_input.text().strip())
            out_p = vault.export_entries(self.filtered_entries, self.key_input.text().strip(), save_path, fmt)
            QMessageBox.information(self, "匯出成功", f"已成功匯出 {len(self.filtered_entries)} 筆機密至：\n{out_p}")
            self.status_bar.showMessage(f"匯出完成: {out_p.name}")

    def _delete_selected_secret(self):
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.filtered_entries):
            QMessageBox.warning(self, "提示", "請先在列表中選取要刪除的機密！")
            return

        entry = self.filtered_entries[current_row]
        name_repr = entry.title or entry.secret
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要自保險庫中永久刪除此機密嗎？\n\n標題: {name_repr}\n行號: L{entry.line_number}\n內容: {entry.secret}\n\n此動作無法還原！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            vault = VigenereVault(self.file_input.text().strip())
            vault.delete_by_line_numbers([entry.line_number])
            QMessageBox.information(self, "成功", "該機密已自保險庫中刪除！")
            self.query_secrets()

    def _add_structured_secret(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "警告", "請先在上方輸入主金鑰 (Key)！")
            self.key_input.setFocus()
            return

        secret = self.add_secret_input.text().strip()
        if not secret:
            QMessageBox.warning(self, "警告", "請輸入機密文字！")
            return

        title = self.add_title_input.text().strip()
        cat = self.add_cat_combo.currentText().strip() or "General"
        tags_raw = self.add_tags_input.text().strip()
        tags_list = [t.strip().lstrip("#") for t in tags_raw.split(",") if t.strip()]

        vault = VigenereVault(self.file_input.text().strip())
        entry = vault.add_secret(key, secret, title=title, tags=tags_list, category=cat)

        self.add_secret_input.clear()
        self.add_title_input.clear()
        self.add_tags_input.clear()
        self._update_vault_file_status()

        QMessageBox.information(
            self, "新增成功",
            f"機密已成功加密寫入！\n標題: {entry.title or '(無)'}\n類型: {entry.category}\n行號: L{entry.line_number}"
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
