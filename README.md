# Cypher - 資訊安全與密碼學技術庫

本專案主要用於整理與存放各類**資訊安全（Cybersecurity）**與**密碼學（Cryptography）**相關的技術實作、演算法、工具與研究資源。

---

## 核心模組：Vigenère Vault 2.0

`vigenere-vault` 是一個結合古典密碼學演算法與現代資安防禦思維的機密管理器，支援在單一加密文字檔（`Secrets.txt`）中儲存多組不同金鑰的機密，具備**可抵賴性（Plausible Deniability）**、**隨機加鹽（Salt / Nonce）**與**非週期性金鑰流延伸**等特性。

---

## 核心技術全景 (Technologies Involved)

| 領域 | 核心技術 | 說明與資安效益 |
| :--- | :--- | :--- |
| **古典密碼** | **擴充版維吉尼亞密碼 (Extended Vigenère)** | 支援大小寫英文字母（$mod\ 26$）與 33 種常見 ASCII 特殊符號集合（$mod\ 33$）的雙軌位移代換。 |
| **密碼學 KDF** | **SHA-256 偽隨機流位移 (Keystream PRNG)** | 以 $\text{SHA256}(\text{Salt}_8 + \text{Key})$ 產生 64 位元十六進位字串作為位移量，消滅傳統維吉尼亞密碼的循環週期性。 |
| **語意安全** | **8 位數 CSPRNG 隨機加鹽 (Nonce / Salt)** | 每次加密透過 `secrets.randbelow` 產生獨立 8 位數隨機碼，確保相同明文每次加密產生的密文皆不同，徹底防禦彩虹表與重送比對。 |
| **資料隔離** | **明文前綴驗證與可抵賴性 (Plausible Deniability)** | 密文格式為 `Salt(8) + Encrypt(Key + Secret)`。僅持有正確 Key 的使用者能通過前綴檢驗並解密，多位使用者的資料共存於同一個檔案且互不知曉對方的存在。 |
| **桌面 GUI** | **PySide6 (Qt 6.12)** | 跨平台高效能桌面介面，具備信號槽（Signals & Slots）架構、QSS 暗黑科技玻璃主題、即時關鍵字過濾搜尋與系統剪貼簿整合。 |
| **終端 CLI** | **Rich & Argparse 雙模架構** | 支援彩色終端面板與格式化表格；支援 `list`、`add`、`delete`、`export` 子指令供腳本自動化，並透過 `getpass` 隱藏金鑰輸入防側錄。 |
| **原生打包** | **PyInstaller macOS .app Bundle** | 透過專屬 `build.py` 一鍵將 Python 與 Qt6 依賴封裝為獨立雙擊即開的 `.app` 桌面軟體，支援路徑自適應。 |

---

## 開啟與執行方式 (How to Launch & Run)

### 0. 安裝環境依賴 (Prerequisites)
```bash
pip install -r vigenere-vault/requirements.txt
```
> 依賴套件包含 `PySide6`（Qt6 GUI 庫）與 `rich`（終端美化庫）。

---

### 1. 雙擊開啟獨立桌面軟體（macOS .app，最推薦）
若您想直接以點兩下圖示的方式打開，可以使用專案內建的打包腳本進行一鍵編譯：

```bash
python vigenere-vault/build.py
```
- **開啟方式**：編譯完成後，至 `vigenere-vault/dist/` 目錄中，對著 **`VigenereVault.app` 直接雙擊點兩下**即可開啟！
- **在 Finder 中定位 App**：
  ```bash
  open -R vigenere-vault/dist/VigenereVault.app
  ```

---

### 2. 透過原始碼啟動現代桌面視窗 (PySide6 GUI)
直接在終端機執行：
```bash
python vigenere-vault/gui.py
```
**GUI 主要功能**：
- **解密清單**：輸入 Master Key 後即時解密，並可透過上方搜尋列進行即時關鍵字搜尋。
- **一鍵複製**：雙擊任意一筆機密或點選「📋 複製選取機密」即可直接存入系統剪貼簿。
- **多格式匯出**：一鍵將解密結果匯出為 Markdown 筆記（`.md`）或純文字檔（`.txt`）。
- **批次新增**：提供多行文字輸入區塊，一次加密多筆資料並自動為每筆資料分配獨立 Salt。

---

### 3. 使用進階彩色終端工具 (CLI)

#### 互動式彩色選單：
```bash
python vigenere-vault/cli.py
```

#### 腳本與命令列子指令（適合終端自動化）：
```bash
# 1. 查詢並列出屬於特定金鑰的機密表格
python vigenere-vault/cli.py list -k "你的Key"

# 2. 查詢並直接匯出為 Markdown 檔案
python vigenere-vault/cli.py list -k "你的Key" --export my_secrets.md --format md

# 3. 新增一筆機密
python vigenere-vault/cli.py add -k "你的Key" -s "github_pat_123456"

# 4. 刪除特定行號的機密
python vigenere-vault/cli.py delete -k "你的Key" -l 3
```

---

### 4. 傳統控制台互動選單
```bash
python vigenere-vault/main.py
```
支援選單式引導建立加密檔、查詢解密、新增/刪除機密，亦可帶參數 `--gui` 或 `--cli` 快速切換模式。

---

## 專案詳細技術文件庫 (Documentation)

更深入的技術理論、密碼學淵源、攻擊面分析與未來路線圖請參閱：

- [**專案全方位技術與架構手冊 (docs/technologies-and-architecture.md)**](./docs/technologies-and-architecture.md)：包含數學公式、信號槽、QSS 樣式體系與軟體工程細節。
- [**技術分析與密碼學淵源報告 (vigenere-vault/docs/technical-analysis.md)**](./vigenere-vault/docs/technical-analysis.md)：古典密碼對照、四步演化心智模型與已知明文攻擊（KPA）分析。
- [**開發待辦清單與路線圖 (vigenere-vault/TODO.md)**](./vigenere-vault/TODO.md)：未來規劃（Argon2id KDF、AES-256-GCM、自動鎖定計時器等）。

---

## 注意事項與安全聲明

1. 本專案僅供資訊安全技術研究、密碼學教育與個人概念驗證（PoC）學習用途。
2. 敏感資料檔案（如 `Secrets.txt`、`decodedSecrets.*`）已由 `.gitignore` 嚴密排除，**請勿將任何真實機密檔案提交至公開版本庫**。
