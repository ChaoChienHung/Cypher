# Cypher 技術文件庫 (Documentation)

本目錄存放本專案各個資安與密碼學模組的技術規格、學術理論對照、密碼分析報告與架構手冊。

---

## 核心文件清單

### 1. 全域技術與架構手冊
- [**專案全方位技術與架構手冊 (technologies-and-architecture.md)**](./technologies-and-architecture.md)
  - 密碼學技術與演算法（擴充維吉尼亞、SHA-256 串流、8-digit CSPRNG Salt、多金鑰隔離）
  - 桌面 GUI 架構（PySide6 / Qt 6、信號槽、QSS 暗黑主題、即時搜尋、剪貼簿）
  - 終端機進階技術（Rich 彩色表格、雙模 Argparse CLI、安全遮罩輸入）
  - 軟體工程與防禦細節（行號消歧義、字首安全剝除、多層 Git 忽略防護）
  - 完整技術矩陣一覽表

### 2. Vigenère Vault 專題分析
- [**技術分析與密碼學淵源報告 (vigenere-vault/docs/technical-analysis.md)**](../vigenere-vault/docs/technical-analysis.md)
  - 歷史與業界前身對照（古典密碼、串流密碼、IV/Nonce、可抵賴加密）
  - 四步演化心智模型（The 4-Step Evolutionary Mindset）
  - 駭客探索思維 vs 工業軍規標準對照表
  - 密碼分析觀點（已知明文攻擊面、位移熵限制、改進方向）
