# Vigenère Vault (基於加鹽 SHA-256 與維吉尼亞密碼的機密管理工具)

本模組為自製的命令列機密管理器（Secret Manager），結合了隨機加鹽（Salt）、SHA-256 雜湊金鑰延伸、擴充版維吉尼亞密碼（Vigenère Cipher）加解密，以及多金鑰共存隔離的驗證機制。

---

## 核心設計理念與演算法架構

### 1. 隨機加鹽與雜湊延伸 (Salted SHA-256 Key Derivation)
- 每次加密一筆機密時，程式隨機產生一組 **8 位數字隨機碼（Salt / Nonce）**：
  $$\text{hashedString} = \text{SHA256}(\text{RandomNumber}_{8} + \text{Key})$$
- 產生的 SHA-256 16 進位字串（64 字元）作為維吉尼亞密碼的位移金鑰序列。
- **優點**：即使同一個 Key、同一段機密重複加密，產生的密文也完全不同，可有效防禦重送攻擊與預先計算的彩虹表（Rainbow Table）攻擊。

### 2. 擴充版維吉尼亞密碼 (Extended Vigenère Cipher)
- 將 SHA-256 的 16 進位字元（$0 \sim 15$）作為動態位移量。
- 支援字元集包含：
  - 英文字母（保留大小寫 $a-z, A-Z$）
  - 常見特殊符號集合（`!@#$%^&*()-=_+[]{}\|;:'\",./<>?~`` ` 等）

### 3. 金鑰驗證與多金鑰共存隔離 (Compartmentalization & Verification)
- **明文封裝格式**：`Key + Secret`
- **儲存格式**：`RandomNumber(8) + Encrypted(Key + Secret)`
- **解密驗證機制**：
  解密後檢查明文開頭是否為輸入的 `Key`。
  - 若符合：代表金鑰正確，剝離 `Key` 並顯示真正的機密內容。
  - 若不符合：視為其他金鑰所擁有的機密或無效金鑰，靜默跳過。
- **特性**：可以在同一個 `Secrets.txt` 檔案中儲存多組不同使用者或不同用途（不同 Key）的機密，而不會洩漏到底有多少個 Key 存在（具備一定程度的資訊隱匿與隔離效果）。

---

## 功能列表

1. **建立加密機密檔案 (Create Encoded Text)**：
   - 支援輸入自訂檔名與金鑰。
   - 支援同金鑰批次加密多筆機密。
2. **解密機密檔案 (Decode Encoded Text)**：
   - 依據輸入的 Key 解析並過濾屬於該 Key 的所有機密。
   - 支援多種輸出管道：
     - 命令列直接顯示（終端機）
     - 輸出為純文字檔 (`decodedSecrets.txt`)
     - 輸出為 Markdown 筆記格式 (`decodedSecrets.md`)
3. **修改機密 (Modify Encoded Text)**：
   - 新增機密（Append）
   - 刪除特定機密（Selective Removal）

---

## 快速使用

```bash
cd vigenere-vault
python3 main.py
```

### 互動選單說明
```text
Please enter your command:
(1) Create Encoded Text  # 建立新的加密檔案
(2) Decode Encoded Text  # 解密特定 Key 的機密
(3) Modify Encoded Text  # 新增或刪除機密
(4) Exit                 # 離開程式
```

---

## 設計思維與心態演進 (The Cryptographic Mindset)

本實作反映了資安愛好者在探索密碼學時經典的**四步演化心智模型**：

1. **基礎代換**：透過維吉尼亞密碼實現基礎亂碼效果。
2. **克服週期性**：自創利用 SHA-256 雜湊將任意 Key 展開為 64 位的非週期性金鑰流。
3. **語意安全（防彩虹表）**：透過 8 位隨機數（Salt / Nonce）保證相同內容每次加密產生完全不同的密文。
4. **多金鑰隔離與所有權驗證**：利用明文前綴 `Key + Secret` 比對，實現單一檔案內多 Key 隱匿共存（可抵賴加密，Plausible Deniability）。

> 完整理論淵源、駭客思維 vs 工業軍規標準對照、以及密碼分析細節，請參閱 [技術分析與密碼學淵源報告 (docs/technical-analysis.md)](./docs/technical-analysis.md)。

---

## 相關文件

- [技術分析與密碼學淵源報告 (docs/technical-analysis.md)](./docs/technical-analysis.md)：深入分析本實作的核心技術、歷史與業界技術前身對照（古典密碼、串流密碼、可抵賴加密）、設計思維心態、以及密碼分析（Cryptanalysis）安全評估。

---

## 安全性觀察與改進建議

1. **移除字首建議**：
   - 在刪除機密邏輯中使用了 `decrypted.lstrip(key)`，若金鑰的第一個字元與機密內容開頭相同，可能會意外去除機密字元；建議改用 `decrypted[len(key):]` 或 Python 3.9+ 的 `decrypted.removeprefix(key)`。
2. **密碼學演算法強度**：
   - 維吉尼亞密碼本質上屬於字元替換式的多表密碼，適合教學與概念驗證（PoC）；若應用於極高安全性場景，後續可將底層加密模組無縫升級為現代分組加密標準（如 AES-GCM 或 ChaCha20-Poly1305），保留目前優秀的隨機 Salt 與多金鑰隔離設計。
