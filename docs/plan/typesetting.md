# 《深入浅出HDD》排版与构建方案（V1.0 · 2026-11-11）

> 决策：**最终书籍模板采用 `docs/templates/ElegantBook-4.7`**（本地锁定版本，不随系统 TeX Live 更新漂移）。
> 关联：[文档与资产管理规范](document-management.md) · [实施计划](implementation-plan.md) · [书籍结构与构建清单](../../book/book.yaml) · [主文档](../../book/main.tex)

---

## 一、总体方案

- **写作源**：`docs/chapters/*.md`（Markdown，AI 起草 + 作者审校；便于 diff、检索与多人协作）。
- **排版源**：`book/main.tex` + `book/book.yaml` + `book/reference.bib`（ElegantBook 4.7，版本锁定）。
- **生成物**：`book/sections/*.tex`（由 `tools/md2tex.py` 从 Markdown 生成，**禁止手改**）。
- **成品**：`book/build/main.pdf`（16 开，500–600 页目标）；里程碑时导出预览 PDF 到 `book/preview/`。
- **工具链**：pandoc 3.9 + TeX Live/MacTeX 2026（xelatex + biber + latexmk）。已验证本机可完整构建。

```
Markdown 章节 → md2tex.py（去编号/展开交叉引用/pandoc/biblatex）→ sections/*.tex
             → build_book.py（latexmk -xelatex + biber）→ build/main.pdf
```

---

## 二、模板与版式参数

| 项 | 设定 |
|----|------|
| 文档类 | `elegantbook`（本地 `book/elegantbook.cls`，4.7） |
| 选项 | `lang=cn,newtx,10pt,scheme=chinese,bibstyle=gb7714-2015,citestyle=gb7714-2015` |
| 开本 | **16 开 185 mm × 260 mm**（覆盖 ElegantBook 默认 A4） |
| 页边距 | 上/下 22 mm，左/右 20 mm，headheight 2.17 cm，footskip 12 mm |
| 字体 | ctex 中文（macOS 下自动 Songti/Heiti 等）；数学 newtx |
| 标题页 | 书名《深入浅出HDD》、副标题「从磁记录理论到整机实践」、作者罗可/陈进才/卢萍、华中科技大学、版本 0.1 |
| 封面/徽标 | 暂用 ElegantBook 示例素材（`book/assets/cover.jpg`、`logo-blue.png`），出版前替换为定制封面 |
| 参考文献 | GB/T 7714-2015（biblatex + biber），按章 `refsegment` 生成章末参考文献 |
| 编号 | 章自动编号；图/表/公式统一为「章号-序号」（如 5-5、表 5-1、式 5-1） |
| 目录 | 三级（章/节/小节）；导读、小结、习题不编号但入目录 |

---

## 三、写作与排版约定（必须遵守）

### 3.1 章节 Markdown

- 文件：`docs/chapters/chNN-<slug>.md`；frontmatter 含 `title/chapter/status/target_pages/target_hanzi/figures/experiments`。
- 章标题：`# 第 N 章 <章名>`；构建脚本会去掉「第 N 章」前缀，由 LaTeX 按 `chapter` 字段自动编号。
- 节标题：`## N.M <节名> {#sec:N.M}`；`### N.M.K <小节名> {#sec:N.M.K}`。构建脚本去掉数字前缀（LaTeX 自动编号），保留 `{#sec:...}` 标签。
- 不编号节：`## 本章导读 {-}`、`## 本章小结 {-}`、`## 习题 {-}`（自动入目录、不编号）。
- **不要手写「参考文献」节**：章末参考文献由构建脚本按 `[@key]` 引用自动生成。
- 引用：正文用 `[@key]`（对应 `book/reference.bib`）；新增文献先核验 DOI/ISBN 再入库。
- 公式：编号公式用原始 LaTeX 环境，**不要写 `\tag`**（由 LaTeX 自动编号）：
  ```latex
  \begin{equation}
  V(t)=\frac{1}{1+(2t/PW_{50})^{2}}
  \label{eq:5-1}
  \end{equation}
  ```
- 图：`![图题](figures/chNN/figNN-MM-slug.png){#fig:N-MM width=92%}`；图必须由 `code/experiments/` 脚本生成并登记 `figures/manifest.yaml`。
- 表：pipe 表格 + 题注行 `: 表题 {#tab:N-MM}`。
- 交叉引用：正文用 `{{fig:N-MM}}`、`{{tab:N-MM}}`、`{{eq:N-MM}}`、`{{sec:N.M}}`、`{{ch:N}}`；构建脚本转换为 `\ref/\eqref`。
- 代码/实验：`{{code:ch05_pulse_shape}}` → 等宽字体；`{{exp:5-2}}` → 「实验 5-2」。

### 3.2 图件规格

- 分辨率 ≥300 dpi；优先矢量（PDF/SVG→PDF）；位图宽度 ≥1800 px。
- 图宽默认 92% 版心；跨页大图 ≤100%；避免 `height=\textheight` 导致缩放异常。
- 图中中文用 Hiragino Sans GB/PingFang/STHeiti 等可嵌入字体；曲线图由 matplotlib 生成（`hddbook.plotting`）。
- 图注在图下、表注在表上；图/表须标来源与版权（原创/改编自 [n]）。

### 3.3 参考文献

- `book/reference.bib` 为唯一文献库；GB/T 7714-2015 顺序编码。
- 每条文献须核验（DOI/ISBN/标准号）；AI 生成条目一律先核验再入库。
- 章末参考文献由 `refsegment` 自动生成；正文引用编号与文献表由 biber 自动对齐。

---

## 四、构建命令

```bash
# 完整构建（转换 + XeLaTeX + biber + PDF）
python3 tools/build_book.py

# 仅转换 Markdown 为 LaTeX（检查生成结果）
python3 tools/md2tex.py

# 清理构建产物
python3 tools/build_book.py --clean

# 文档/图-代码一致性检查
python3 tools/check_docs.py
```

**环境要求**：pandoc、latexmk、xelatex、biber；TeX Live/MacTeX 2026（已验证）。缺工具时 `build_book.py` 会明确报错。

---

## 五、质量门禁（排版相关）

1. **构建通过**：`build_book.py` 返回 0，PDF 生成；无 `!` 错误。
2. **引用完整**：无 undefined references / citations（latexmk 报告为空）。
3. **文献合规**：章末参考文献由 bib 生成；条目逐条核验；GB/T 7714 格式正确。
4. **编号一致**：图/表/公式编号与正文引用一致；manifest 中的计划编号与最终自动编号的差异须在构建报告中登记。
5. **字体嵌入**：`pdffonts` 检查中文与数学字体已嵌入；无 Type 3 位图字体。
6. **版面检查**：无严重 overfull hbox（>10 pt 需修）；图表不跨页断裂；目录层级正确。
7. **页数核对**：与分章预算累计偏差 ≤10%；M6/M7 核对 500–600 页目标。
8. **元数据**：PDF 标题/作者/版本正确；前言含版权与引用说明。

---

## 六、版本与交付

- 每章完成并通过内容门禁后，构建一次 PDF 做版面检查；不要求每章提交 PDF。
- 里程碑（M0/M1…M7）导出预览：`book/preview/book-v<版本>-<日期>.pdf`，随仓库提交（≤5 MB）。
- 最终交付：`book/build/main.pdf` + 完整源码包（Markdown、LaTeX、图、代码、bib）+ 构建说明。
- 版本号：0.1（样章）→ 0.5（全稿初稿）→ 0.9（审校稿）→ 1.0（交付稿）。

---

## 七、已知限制与后续

1. **部分构建的编/章编号**：只构建部分章节时，`\setcounter{chapter}`/`\setcounter{part}` 已按清单强制编号；最终全量构建须复核目录。
2. **图号漂移**：`figures/manifest.yaml` 使用计划编号（如 `fig:5-5`），LaTeX 按实际顺序自动编号；插入新图会导致后续图号变化，须在定稿前统一核对。
3. **封面**：当前为 ElegantBook 示例封面，出版前替换为定制封面（书名/作者/出版社）。
4. **索引**：ElegantBook 未启用索引；定稿前可加 `\makeindex` + 术语索引。
5. **PDF/A 与印刷**：当前为屏幕阅读 PDF；印刷前需检查出血、CMYK 图、字体嵌入与 PDF/X 合规。
6. **CI**：本机构建已验证；如需 GitHub Actions，需安装 TeX Live + pandoc（体积较大，暂缓）。

---

## 八、首次构建验证记录（2026-11-11）

- 环境：pandoc 3.9.0.2、XeTeX (TeX Live 2026)、latexmk、biber。
- 输入：`docs/chapters/ch05-recording-channel.md`（样章骨架）+ `book/reference.bib`（8 条经典文献）。
- 输出：`book/build/main.pdf`，6 页（封面、目录（含前言）、前言、编扉、章正文、图/表/参考文献）。
- 验证：前言不编号且入目录；章号「第五章」、节号 5.1/5.1.1/5.2、公式 (5-1)、图 5-1、表 5-1、GB/T 7714 参考文献 [1][2] 均正确渲染；无 undefined reference/citation；PDF 元数据（标题/作者/主题）正确；中文字体已嵌入。
- 已知：样章仅 1 幅图，故图号显示 5-1（全章 5 幅图时将为 5-5）；部分构建的编号为「第二部分」（已按清单强制）。
