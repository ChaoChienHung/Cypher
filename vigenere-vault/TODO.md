# Vigenère Vault 專案開發計畫 (TODO)

本清單整理了 `vigenere-vault` 目前已完成的功能里程碑，以及後續在**密碼學安全性強化**、**GUI/CLI 使用者體驗**與**測試驗證**等維度的待辦規劃。

---

## 📌 進行中與規劃中項目 (Planned & Backlog)

### 🔐 密碼學與安全性強化 (Cryptographic Enhancements)
- [ ] **導入慢速金鑰衍生函數 (KDF)**：
  - 現狀：單次 `SHA-256(Salt + Key)` 計算極快，容易被 GPU 暴力破解。
  - 計畫：導入 `Argon2id` 或 `scrypt`，強制增加計算時間與記憶體開銷，有效防禦硬體窮舉攻擊。
- [ ] **升級現代 AEAD 加密模組選項**：
  - 提供 `AES-256-GCM` 或 `ChaCha20-Poly1305` 作為可切換的現代加密後端。
  - 保留原有隨機加鹽與多金鑰共存隔離哲學，但將底層代換密碼提升至軍規標準。
- [ ] **擴充隨機 Nonce 空間**：
  - 現狀：8 位數字隨機碼（約 $9 \times 10^7$ 種可能，約 26.5 bits）。
  - 計畫：擴充為 16 或 32 位元組的十六進位/Base64 隨機 Nonce，徹底消除空間窮舉可能性。
- [ ] **位移量熵（Entropy）全覆蓋**：
  - 現狀：SHA-256 十六進位字元位移量僅 $0 \sim 15$，小於字母表長度（26）造成模數偏差。
  - 計畫：改用 SHA-256 raw bytes（$0 \sim 255$）進行位移計算，達成字母表完全均勻覆蓋。

---

### 🖥️ GUI / 使用者體驗提升 (PySide6 GUI Enhancements)
- [ ] **閒置自動鎖定機制 (Auto-lock Timer)**：
  - 當使用者離開螢幕或視窗閒置超過特定時間（如 5 分鐘），自動清除記憶體中的金鑰與解密列表，保護機密防窺。
- [ ] **金鑰強度即時評分條 (Password Strength Meter)**：
  - 輸入 Master Key 時即時分析長度、字元複雜度與熵值，提供視覺化強度指示。
- [ ] **淺色 / 深色主題切換 (Theme Toggle)**：
  - 支援隨系統外觀自動切換，或在介面提供 Light/Dark 模式切換按鈕。
- [ ] **機密編輯功能 (Edit In-place)**：
  - 允許直接雙擊修改已解密的機密並即時重新加密儲存，無需先刪除再重新新增。
- [ ] **更多格式匯出/匯入 (CSV / JSON)**：
  - 支援結構化備份與匯出，方便與其他密碼管理器（如 Bitwarden、1Password、KeePass）互相遷移。

---

### 💻 CLI 終端功能優化 (CLI Enhancements)
- [ ] **標準輸入/輸出管道支援 (Pipe & Stdin/Stdout)**：
  - 支援 `echo "my_token" | python cli.py add -k "$KEY"` 與 `python cli.py query -k "$KEY" | grep token`。
- [ ] **Shell 自動補全 (Shell Autocomplete)**：
  - 為 Zsh 與 Bash 提供子指令與旗標補全腳本。
- [ ] **全域環境變數與設定檔支援**：
  - 支援 `~/.config/vigenere-vault/config.json` 設定預設保險庫路徑。

---

### 🧪 測試與密碼分析 (Testing & Security Verification)
- [ ] **自動化單元測試套件 (Pytest)**：
  - 涵蓋各種邊界字元、空字串、全特殊符號、多金鑰併發查詢等極端情況。
- [ ] **已知明文攻擊模擬腳本 (Known-Plaintext Attack PoC)**：
  - 撰寫示範 PoC 驗證舊版演算法的密碼分析特徵，作為資安教學研究案例。
- [ ] **效能基準測試 (Benchmark)**：
  - 測試當單一保險庫超過 10,000 筆機密時的查詢與解密效能評估。

---

## ✅ 已完成項目 (Completed)

- [x] **結構化屬性與標籤篩選 (Properties & Tag Filtering)**：
  - 支援 `title`（標題）、`category`（類型）、`tags`（多標籤）與 `created_at`（時間戳記）。
  - 智能 JSON 封裝全欄位加密，並保證對舊版純文字機密 100% 向後相容。
  - PySide6 GUI 與 CLI 同步支援多條件即時過濾（關鍵字、標籤下拉選單、類型過濾）。
- [x] **初始化 Git 版本庫並排除敏感檔案**：
  - 建立 `.gitignore` 排除 `Secrets.txt`、`decodedSecrets.*` 與系統暫存檔。
- [x] **架構重構與模組化 (`core.py`)**：
  - 修正舊版 `lstrip` 誤刪字首問題，改用嚴格的 `[len(key):]` 切割。
  - 解決字典衝突問題，改以實體行號索引定位（`VaultEntry`）。
  - 使用 Python 內建 CSPRNG `secrets.randbelow` 升級 8 位數 Salt。
- [x] **進階彩色終端介面 (`cli.py`)**：
  - 支援 Rich 彩色終端面板與格式化表格。
  - 支援子指令體系（`list`, `add`, `delete`, `export`, `create`）與互動選單。
  - 支援 `getpass` 隱藏式密碼輸入防側錄。
- [x] **現代桌面圖形介面 (`gui.py`)**：
  - 全面採用 PySide6 (Qt 6) 打造科技深色風格視窗。
  - 具備即時搜尋過濾、雙擊複製剪貼簿、金鑰遮罩切換、批次新增與多格式匯出。
- [x] **完整技術文件撰寫 (`docs/`)**：
  - 撰寫技術規格手冊、密碼學歷史對照、四步演化心智模型與攻擊面分析。
