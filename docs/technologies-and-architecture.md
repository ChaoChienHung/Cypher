# Cypher 專案全方位技術與架構手冊 (Technologies & Architecture)

本文件整合了本專案（特別是 `vigenere-vault` 模組及其 PySide6 GUI 與 CLI）所運用的所有**密碼學演算法**、**圖形介面架構**、**終端機技術**與**安全防禦機制**。

---

## 目錄

1. [密碼學技術與演算法 (Cryptography)](#一密碼學技術與演算法-cryptography)
2. [桌面 GUI 架構與技術 (Qt6 & PySide6)](#二桌面-gui-架構與技術-qt6--pyside6)
3. [CLI 終端機進階技術 (Rich & CLI)](#三cli-終端機進階技術-rich--cli)
4. [軟體架構與資安工程細節](#四軟體架構與資安工程細節)
5. [技術矩陣一覽表](#五技術矩陣一覽表)

---

## 一、密碼學技術與演算法 (Cryptography)

### 1. 擴充版維吉尼亞多表代換密碼 (Extended Vigenère Cipher)
- **原理**：古典維吉尼亞密碼僅支援 26 個英文字母；本系統擴充為支援：
  - 英文字母：大小寫各自分離位移，模數運算為 $26$：
    $$\text{Cipher}_i = (\text{Plain}_i + \text{Shift}_i) \pmod{26}$$
  - 特殊字元集：自定義包含 33 個常見符號與空格的集合（`!@#$%^&*()-=_+[]{}\|;:'",./<>?~` 與空格），模數運算為 $33$：
    $$\text{Cipher}_i = (\text{Plain}_i + \text{Shift}_i) \pmod{33}$$
- **解密位移逆轉**：
  $$\text{Plain}_i = (\text{Cipher}_i - \text{Shift}_i) \pmod N$$

### 2. SHA-256 雜湊金鑰延伸流 (Hash-based Keystream PRNG)
- **原理**：古典維吉尼亞密碼因金鑰長度固定，具有重複週期性，極易被卡西斯基試驗（Kasiski Examination）破譯。
- **改進技術**：利用 SHA-256 雜湊演算法將 `Salt(8) + Key` 映射為 64 個十六進位字元序列：
  $$\text{Keystream} = \text{SHA256}(\text{Salt}_8 + \text{Key}) \in [0, 15]^{64}$$
  每個字元換算為 $0 \sim 15$ 的整數位移量，徹底消除固定詞彙重複週期。

### 3. 8 位數安全加鹽 (CSPRNG Nonce / Salt)
- **技術**：使用 Python 內建的密碼學安全偽隨機數產生器 `secrets.randbelow(90000000) + 10000000` 生成 $10000000 \sim 99999999$ 的隨機數字。
- **資安目的**：
  - **語意安全（Semantic Security）**：保證即使使用相同金鑰重複加密同一段明文，產生的密文也完全不同。
  - **抗彩虹表（Anti-Rainbow Table）**：使預先計算雜湊碰撞字典的攻擊完全失效。

### 4. 明文前綴驗證與可抵賴多租戶隔離 (Plausible Deniability)
- **密文封裝格式**：
  $$\text{Line} = \text{Salt}_8 + \text{Encrypt}_{\text{Keystream}}(\text{Key} + \text{Secret})$$
- **驗證原理**：解密時檢驗明文字首是否以 `Key` 開頭：
  - **相符**：驗證成功，剝除 `Key` 前綴並呈現真實明文。
  - **不相符**：代表該筆機密屬於其他使用者（其他 Key）或密鑰錯誤，程式靜默略過。
- **資安效益**：在單一檔案內達成隱蔽式多金鑰共存隔離，外部攻擊者無法確認檔案中究竟存在幾組 Key 或多少別人的機密。

---

## 二、桌面 GUI 架構與技術 (Qt6 & PySide6)

本專案 GUI 放棄了依賴環境 Tcl/Tk 的 Tkinter，全面升級為官方 **Qt 6 for Python (PySide6)**，採用專業級軟體架構：

### 1. 信號與槽機制 (Signals & Slots)
- Qt 的事件驅動核心模式。將 UI 互動（如按鈕點擊 `clicked`、文字變更 `textChanged`、按下 Enter `returnPressed`、表格雙擊 `doubleClicked`）與核心邏輯解耦。
- 實現了高響應性的即時交互體驗。

### 2. QSS (Qt Style Sheets) 深色暗黑主題系統
- 基於類似 CSS 語法構建的現代深色玻璃風格（Cyber Dark Theme）：
  - 底色採用 Slate 黑底（`#121318`、`#1A1C23`）。
  - 強調色採用科技亮青色（`#0284C7`、`#38BDF8`）。
  - 危險操作（刪除）使用低飽和緋紅（`#881337`、`#9F1239`）。
  - 邊角圓弧化（`border-radius: 6px ~ 10px`），大幅提升視覺現代感。

### 3. 模型與表格管理 (QTableWidget)
- 採用 4 欄式結構：`#`（流水號）、`保險庫行號`、`隨機鹽值 (Salt)`、`解密明文 (Plaintext)`。
- 表格行為自訂：單列整行選取（`SelectRows`）、唯讀保護（`NoEditTriggers`）、彈性寬度延展（`QHeaderView.ResizeMode.Stretch`）。
- 雙擊任意列直接複製機密至剪貼簿。

### 4. 即時全文過濾演算法 (Real-time Filter Subsetting)
- 監聽 `QLineEdit.textChanged` 信號，每當使用者輸入字元時，立即在記憶體中的 `cached_entries` 執行不區分大小寫的子字串比對，並動態重新渲染表格，毋需重新解密或存取硬碟。

### 5. 安全性防護與系統剪貼簿 (Security & Clipboard)
- **密碼防窺探**：金鑰輸入框預設啟用 `QLineEdit.EchoMode.Password`，並可透過核取方塊切換顯示。
- **剪貼簿整合**：透過 `QApplication.clipboard()` 提供一鍵複製功能，免除人工選取文字的繁瑣與失誤。
- **防呆對話框**：刪除機密時彈出二次確認模態視窗（`QMessageBox.question`），防範誤刪。

---

## 三、CLI 終端機進階技術 (Rich & CLI)

`cli.py` 提供專業級的終端操作介面，支援互動與非互動兩種工作模式：

### 1. 雙模架構 (Dual-Mode Design)
- **非互動模式 (Argparse Subcommands)**：支援 `list`、`add`、`delete`、`export`、`create` 等子指令，能無縫整合至 Shell 腳本、CI/CD 流程或管線處理（Piping）。
- **互動選單模式 (Interactive Menu)**：無參數執行時自動啟動美化互動控制台。

### 2. Rich 彩色終端渲染
- 採用 `rich.table.Table`、`rich.panel.Panel`、`rich.prompt` 輸出格式化表格與提示。
- 支援色彩高亮、邊框樣式設定與直觀的欄位對齊。

### 3. 隱藏式金鑰輸入 (Secure Input)
- 在終端機下使用標準函式庫 `getpass.getpass()` 輸入主金鑰，避免金鑰出現在終端螢幕、Shell History 或螢幕錄影中。

---

## 四、軟體架構與資安工程細節

### 1. 消除字首剝除 Bug (`lstrip` $\rightarrow$ `removeprefix`)
- **舊版瑕疵**：舊版使用了 `decrypted.lstrip(key)`。若 Key 為 `admin`，機密明文為 `apple`，`lstrip('admin')` 會將 `apple` 的首字母 `a` 一併削去，變成 `pple`。
- **新版架構**：`core.py` 改用嚴格切片 `decrypted[len(key):]`，徹底杜絕非預期的明文字元遺失。

### 2. 行號定位機制 (Row Disambiguation)
- 舊版刪除功能使用字典 `Dict[secret, line]`，若使用者同一個 Key 下有兩筆相同的機密，後者會覆蓋前者造成字典鍵衝突。
- 新版使用 `VaultEntry(line_number, salt, secret, raw_line)`，以檔案實體行號（Line Number）作為唯一識別碼，確保重複資料也能精準定位與刪除。

### 3. Git 忽略多層防護 (`.gitignore`)
- 根目錄 `.gitignore` 採用通配符規則：
  ```gitignore
  Secrets.txt
  **/Secrets.txt
  decodedSecrets.txt
  decodedSecrets.md
  **/decodedSecrets.*
  ```
- 徹底防止任何子目錄內的加密檔案或解密明文產出檔被誤提交至公開 Git 版本庫。

---

## 五、技術矩陣一覽表

| 技術項目 | 採納技術 / 函式庫 | 用途與優勢 |
| :--- | :--- | :--- |
| **雜湊演算法** | `hashlib.sha256` | 產生 256 位元偽隨機金鑰流 |
| **安全隨機數** | `secrets.randbelow` | 生成 8 位數不可預測的 Salt |
| **核心 GUI** | **PySide6 (Qt 6.12)** | 跨平台、高效能、支援 Retina 高解析度的原生桌面 GUI |
| **GUI 樣式** | **QSS (Qt Style Sheets)** | 科技暗黑視覺主題與自訂組件外觀 |
| **終端美化** | **Rich** | 終端彩色面板、彩色表格與格式化提示 |
| **參數解析** | `argparse` | 支援子指令體系的現代 CLI 架構 |
| **隱藏輸入** | `getpass.getpass` | 終端機密碼輸入防側錄 |
| **資料載體** | `@dataclass (VaultEntry)` | 乾淨、具備型別提示的機密物件封裝 |
| **原生打包編譯** | **PyInstaller** | 將 Python + PySide6 打包成雙擊即開的 macOS `.app` Bundle |

---

## 六、獨立應用程式打包與編譯技術 (Application Bundling)

本專案提供專門的打包編譯腳本 `build.py`，能自動將 Python 原始碼與 PySide6 依賴項封裝成 macOS 原生應用程式（`.app` Bundle），支援使用者直接雙擊執行：

### 1. macOS `.app` Bundle 結構
PyInstaller 透過 `--windowed` 參數產生符合 Apple 標準的應用程式套件結構：
```
VigenereVault.app/
└── Contents/
    ├── Info.plist           # 包含 Bundle Identifier、版本與作業系統相容設定
    ├── MacOS/
    │   └── VigenereVault    # 獨立二進位 Mach-O 啟動執行檔
    ├── Resources/           # 應用程式資源與圖示
    └── Frameworks/          # 內嵌之 Python Runtime 與 Qt6 動態函式庫
```

### 2. Frozen Runtime 環境探測
當應用程式被打包後，Python 解譯器會設定 `sys.frozen = True`。程式透過此旗標動態調整工作路徑，自動選取使用者的桌面或家目錄尋找 `Secrets.txt`，確保雙擊啟動時不會因路徑偏差而找不到檔案。
