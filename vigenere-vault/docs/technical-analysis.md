# Vigenère Vault 技術分析與密碼學淵源

本文詳細剖析 `vigenere-vault` 所採用的各項技術、密碼學歷史對照、學術理論淵源，以及該設計在密碼分析（Cryptanalysis）角度的特性。

---

## 一、系統架構與技術拆解

本系統的運作本質上是一個 **「加鹽雜湊串流化」的擴充型多表代換密碼（Salted Hash-Driven Polyalphabetic Stream Substitution）**，主要由以下四個核心機制組成：

### 1. 隨機加鹽 (Random Salt / Nonce)
- **實作方式**：每次加密時透過 `random.randint(10000000, 99999999)` 產生 8 位數字。
- **密碼學角色**：充當密碼學中的 **初始化向量（IV, Initialization Vector）** 或 **隨機數（Nonce, Number used once）**。
- **目的**：保證語意安全（Semantic Security）。即使同一個使用者用相同的金鑰加密相同的內容，產生的密文也完全不同，徹底消除預先計算的彩虹表攻擊與重送比對。

### 2. SHA-256 雜湊金鑰流延伸 (Hash-based Keystream Generation)
- **實作方式**：將 `RandomNumber(8) + Key` 輸入 SHA-256，計算其十六進位字串（64 個十六進位字元，每個字元值介於 $0 \sim 15$）。
- **密碼學角色**：扮演 **金鑰衍生函數（KDF, Key Derivation Function）** 與 **偽隨機金鑰流產生器（PRNG / Keystream Generator）**。

### 3. 擴充版維吉尼亞密碼 (Extended Vigenère Cipher)
- **實作方式**：
  - 英文字母：根據十六進位值 $0 \sim 15$ 在字母表內做模數加法（$\text{shift} \pmod{26}$）。
  - 特殊字元：自定義包含 32 個常見特殊符號與空格的列表，同樣進行循環模數加法（$\text{shift} \pmod{32}$）。
- **密碼學角色**：古典對稱式多表代換密碼（Polyalphabetic Substitution Cipher）。

### 4. 明文前綴驗證與多金鑰隔離 (Prefix Verification & Compartmentalization)
- **實作方式**：加密前將明文組裝為 `Key + Secret`。解密時若前綴符合 `Key`，則視為金鑰正確並移除前綴。
- **密碼學角色**：訊息完整性與身分驗證標籤（類似 Authentication Tag），並實現了**密文共存與資訊隱匿（Plausible Deniability）**。

---

## 二、「這是不是已經有人用過的技術？」—— 歷史與理論淵源

答案是：**構成這套系統的「各個核心觀念」在密碼學歷史與現代資安中都有非常深厚的理論基礎與廣泛應用，但你把它們拼裝出來的方式極具原創性與巧思！**

具體對照如下：

### 1. 維吉尼亞密碼（Vigenère Cipher）—— 16 世紀古典密碼之王
- **歷史**：最早於 1553 年由義大利密碼學家 Giovan Battista Bellaso 提出，後因 Blaise de Vigenère 於 1586 年提出自金鑰密碼而得名。曾經有三個世紀被認為是「不可破譯的密碼（Le Chiffre Indéchiffrable）」。
- **破譯歷史**：1863 年 Friedrich Kasiski 發表了卡西斯基試驗（Kasiski Examination），利用重複字詞間隔找出金鑰長度並結合字母頻率分析破解。
- **你的改進**：傳統維吉尼亞密碼的金鑰通常是簡短的單詞（重複週期短）；而你使用 SHA-256 產生 64 位元的非週期性十六進位序列，並引入隨機 Salt，使得傳統的卡西斯基分析無法直接生效。

### 2. 雜湊當作串流產生器（Hash as Keystream Generator）—— 串流密碼的現代雛形
- **現代對照**：現代密碼學中的 **串流密碼（Stream Cipher，如 RC4, Salsa20, ChaCha20）**，本質上就是用一個演算法將簡短的金鑰與 Nonce 擴展成極長的偽隨機數流（Keystream），再將金鑰流與明文做 XOR 或代換運算。
- 用 SHA 系列雜湊函數來充當偽隨機產生器（如 ANSI X9.31、Hash-based PRNG、OFB 模式）在工業界有非常多標準方案。你的寫法在概念上正是**「自己手工實作了一個以 SHA-256 為 PRNG 的串流加密器」**。

### 3. 隨機加鹽 (Salt / Nonce) —— 現代加密標準不可或缺的基石
- **現代對照**：早期 WEP 無線加密的 24-bit IV、TLS 協定中的 Client/Server Random、AES-GCM 中的 96-bit Nonce、以及密碼雜湊中的 bcrypt / Argon2 Salt。
- 每次加密在密文前端存放明文隨機數的做法，正是密碼學中最標準、最被廣泛推薦的設計。

### 4. 明文前綴驗證與多金鑰共存隔離 —— 類似 TrueCrypt / VeraCrypt 的隱蔽設計
- **現代對照**：
  1. **魔術標頭驗證（Magic Bytes）**：在密文解密前檢查特定特徵，在很多早期協定與檔案格式中很常見。
  2. **可抵賴加密（Plausible Deniability）**：著名的硬碟加密軟體 TrueCrypt / VeraCrypt 擁有「隱藏卷（Hidden Volume）」技術——外人拿到加密硬碟只看得到雜湊亂碼，不知道裡面究竟有幾個密碼，輸入密碼 A 就只開出 A 的文件，輸入密碼 B 就開出 B 的文件。
  3. 你的設計正是達到了這個效果：同一個 `Secrets.txt` 檔案可以儲存多個不同人的機密，彼此無法得知別人的金鑰，也無法確認檔案裡到底有誰的機密。

---

## 三、密碼分析（Cryptanalysis）角度的安全性檢視

若以嚴格的密碼學角度來分析這套實作，有以下特點與潛在攻擊面值得探討：

### 1. 已知明文攻擊風險（Known-Plaintext Attack, KPA）
- **現象**：因為明文的前綴固定是 `Key`，而密文的前段是 `Encrypted(Key)`。
- **影響**：攻擊者若知道加密演算法，且知道密文的開頭幾位是 `Key` 的代換結果，就可以直接推算出金鑰流的前幾個位移量：
  $$\text{shift}_i = (\text{ciphertext}_i - \text{key}_i) \pmod M$$
- 雖然推導出部分金鑰流不代表能輕易逆向 SHA-256（因為 SHA-256 具有單向性 Pre-image Resistance），但直接暴露了部分內部狀態。

### 2. 位移量熵（Entropy）有限
- **現象**：十六進位字元的整數值只有 $0 \sim 15$。
- **影響**：英文字母有 26 個，特殊字元有 32 個。當位移量最大只有 15 時：
  - 英文字母無法位移超過 15 個位置（例如 `'a'` 只能變成 `'a'` 到 `'p'` 之間的字母，不可能變成 `'q'` 到 `'z'`）。
  - 這造成密文輸出具有嚴重的**統計偏差（Statistical Bias）**，攻擊者即使沒有金鑰，也能依此縮小搜尋空間。
- **解決方案**：直接使用 SHA-256 的 raw bytes（$0 \sim 255$），或是將兩個十六進位字元合併成一個 byte 運算。

### 3. 隨機數空間大小
- **現象**：8 位數字隨機數（$10^7$ 到 $10^8$，約 $9 \times 10^7$ 種可能）。
- **影響**：約等於 $26.5 \text{ bits}$ 的空間。在現代電腦的算力下（每秒數億次 SHA-256 運算），若使用者的金鑰長度較短，攻擊者可透過暴力窮舉（Brute-force）在短時間內遍歷這 $9 \times 10^7$ 個隨機數。
- **解決方案**：增加 Nonce 長度（例如 16 位元組隨機位元），並改用安全隨機數產生器 `secrets.token_bytes()` 取代非密碼學等級的 `random` 模組。

---

## 四、設計心態與演化思維 (The Cryptographic Mindset & Convergent Evolution)

這套系統最引人入勝的地方不在於單一演算法，而在於其背後反映出的 **密碼學工程思維路徑**。這種自發性探索呈現了極客社群中常見的「思維趨同演化」。

### 1. 四步演化心智模型 (The 4-Step Evolutionary Mindset)

當一位具備資安直覺的開發者試圖從零建構機密儲存庫時，大腦通常會經歷以下四個遞進階段：

```
[階段 1: 基礎加密]
  需求: 將文字變成看不懂的亂碼
  思維: 採用古典的維吉尼亞/凱撒代換法。
       ↓
[階段 2: 克服週期性]
  發現: 短金鑰會重複循環，頻率分析輕易破譯。
  思維: 利用 SHA-256 雜湊將任意金鑰展開成 64 字元的偽隨機流。
       ↓
[階段 3: 追求語意安全]
  發現: 相同明文與密碼加密結果固定，容易遭受彩虹表與重送攻擊。
  思維: 在加密前注入隨機產生的 8 位數 Salt/Nonce，確保每次密文皆獨一無二。
       ↓
[階段 4: 身分驗證與多金鑰隔離]
  發現: 解密時不知道使用者密碼是否正確，且想在同一個檔案存放不同人的機密。
  思維: 在明文前綴加入 Key 做為驗證錨點；符合者剝除前綴，不符者靜默略過。
```

### 2. 工業防禦思維 vs. 實驗探索思維 (Industrial Mindset vs. Hacker PoC Mindset)

在密碼學界著名的原則是 **"Don't roll your own crypto"（切勿自製密碼演算法）**。下表對比了個人實驗的直覺思維與工業界標準防禦思維的差異：

| 考量維度 | 實驗探索思維 (PoC / Hacker Mindset) | 工業級防禦思維 (Production / Military Standard) | 差異關鍵原因 |
| :--- | :--- | :--- | :--- |
| **金鑰衍生 (KDF)** | `SHA256(Salt + Key)` | **Argon2id** / **PBKDF2** | SHA 運算過快，GPU 每秒可算百億次；工業標準強制加入計算時間與記憶體門檻以抗窮舉。 |
| **加密核心** | 擴充版維吉尼亞字元替換 | **AES-256-GCM** / **ChaCha20** | 維吉尼亞密碼有十六進位模數偏差（0~15），無法均勻覆蓋字母表；標準加密具備完全擴散與混淆。 |
| **完整性驗證** | 明文塞入 `Key` 前綴 (`Key + Secret`) | **AEAD 驗證標籤 (Poly1305 / GHASH)** | 在明文中放置已知金鑰會產生已知明文洩漏（KPA）；AEAD 提供數學證明不可偽造的獨立 Tag。 |
| **隨機性來源** | 標準函式庫 `random.randint` | **密碼學安全隨機數 (CSPRNG, `secrets` / `/dev/urandom`)** | `random` 是線性同餘或梅森旋轉演算法，其內部狀態在累積一定輸出後可被完全推算。 |
| **多金鑰隔離** | 前綴比對失敗靜默跳過 | **可抵賴加密 (Plausible Deniability)** | 兩者哲學高度一致（如 VeraCrypt 隱藏卷），皆達到「外界無法得知檔案內含多少組金鑰」的隱蔽效果。 |

### 3. 未來架構升級地圖 (Evolutionary Upgrade Path)

這套系統的架構骨幹（Salt + Keystream + Verification + Multi-key Coexistence）非常完整。若未來希望將其重構成生產環境等級的保險庫，只需替換核心原語，互動層與架構完全不需改動：

1. **隨機數升級**：將 `random.randint` 替換為 `secrets.token_bytes(16)`。
2. **KDF 升級**：引入 `hashlib.scrypt` 或 `argon2_cffi`，將密碼延展成 256-bit 高強度主金鑰。
3. **密碼演算法升級**：使用 `cryptography.hazmat.primitives.ciphers.aead.AESGCM`。
4. **隔離升級**：利用 AES-GCM 的驗證失敗異常（`InvalidTag`）取代明文前綴比對；當 Key 錯誤時解密會直接丟出異常，代表該筆資料非當前金鑰所有，同樣達成多金鑰隔離效果且不洩漏明文！

---

## 五、總結

> **「這套機制是古典密碼學、現代資安概念與極客直覺的精彩交會。」**

- **歷史與業界淵源**：加鹽防彩虹表、金鑰流生成、多租戶資料隔離與可抵賴性，皆為密碼學殿堂的核心題目。
- **獨創性與價值**：作為個人探索與資安 PoC，該實作展現了高度一致且嚴密的密碼學演進思維，是絕佳的資安技術學習教具與概念驗證原型。
