# 《深入浅出HDD》编著文档

本书为**中国大陆首部尽可能深入介绍机械硬盘（HDD）整机技术的专业技术书籍**。

## 文档索引

| 文档 | 说明 |
|------|------|
| [图书方案与章节提纲](plan/book-outline.md) | 书籍定位、目标读者、撰写风格、**18 章**全面型提纲、素材覆盖核对、定稿决策、素材索引（**主文档**） |
| [实施计划](plan/implementation-plan.md) | 篇幅与产能基线、分章预算、写作顺序与依赖、24 周排期与里程碑、单章流水线、写作规范、质量门禁、风险对策（**执行主文档**） |
| [进度追踪](plan/progress.md) | 章节状态、字数/图数/门禁统计、里程碑与周报（唯一进度真源） |
| [独立评审意见](plan/plan-review.md) | 对提纲结构与实施可行性的独立评审（阻断项/重要项/建议项） |
| [素材核验](plan/material-audit.md) | 逐章素材落点核验、汉字/图数统计、素材充足度与扩写倍率 |
| [知识资产总图](plan/knowledge-assets.md) | 译稿/知识库/论文库/实验项目/报告/实测数据的资产地图、章节映射、使用规程与合规风险 |
| [实验资产清单](plan/experiment-inventory.md) | 17 个本地实验/代码项目的用途、入口、测试、许可与移植评估 |
| [知识库核验](plan/knowledge-base-inventory.md) | OpenKnowledgeBase 检索链、References 分类、IEEEtran 自著论文、项目报告与数据可用性 |
| [实验与代码体系](plan/experiments.md) | 章节实验矩阵、代码架构、复现验收标准、迁移计划、版权处置 |
| [文档与资产管理规范](plan/document-management.md) | 目录/命名/元数据/台账/图-代码映射/审校/版本管理规范 |
| [排版与构建方案](plan/typesetting.md) | ElegantBook 4.7 最终模板、16 开版式、Markdown→LaTeX→PDF 构建管线、编号/引用/图件规范与排版门禁 |
| [资产台账](plan/asset-registry.csv) | 资产逐条台账（类型/路径/许可/章号/用法/状态/风险） |
| [第 5 章详细大纲（样章）](plan/ch05-outline.md) | 样章节/小节结构、公式/图/习题/文献清单、素材落点与仿真设计 |
| [章节内容与素材确认单（模板）](plan/chapter-brief-template.md) | 每章动笔前须填写的定位/边界/节结构/素材来源/待确认项模板 |
| [第 5 章内容与素材确认单](plan/ch05-brief.md) | 第 5 章边界、节结构、来源（含行号）、图/表/实验清单与 6 项待确认问题 |
| [定时恢复资产包](plan/assets-timing-recovery.md) | Rice 数字通信译本（Ch8/附录 C）、MATLAB 参考实现与 PSP 的资产清单、勘误协议、术语映射与第 8 章骨架 |
| [Rice 译本勘误登记](plan/errata-digital-communications.md) | 已确认勘误 E-01~E-06、待核项 V-01~V-06 与写作红线 |
| [章节写作模板](templates/chapter-template.md) | 统一章节结构、写作标记、交付前自检清单 |
| [排版模板（ElegantBook 4.7）](templates/ElegantBook-4.7/README.md) | LaTeX 书籍排版模板（ElegantBook），用于后期排版与 PDF 生成 |
| [实验与代码库](../code/README.md) | 共享库 `hddbook/`、章节实验脚本、测试与数据规范 |

## 编著约定

- **章节主体**：以磁记录读写信道/信号处理为主线（Piya 三卷本 + 《磁记录系统的编码与信号处理》），并纳入伺服定位/机电控制/主轴电机等整机关键技术。
- **目标读者**：数据存储专业研究生 + 产业工程师。
- **撰写风格**：深入浅出教学型，学术准确性优先，兼顾工程落地，每章小结 + 习题。
- **总篇幅**：约 500–600 页（中大型，已定稿）；正文约 31.4 万汉字、图约 320 幅，分章预算见实施计划。
- **素材指引**：见 `plan/book-outline.md` 第八节的素材索引与第六节的覆盖核对；逐章素材充足度见 `plan/material-audit.md`。
- **版权**：前言设「素材版权与引用说明」，厂商/IEEE 图原创重绘；改写处标注来源。
- **写作纪律**：不得整段照搬译稿；AI 起草内容须经作者逐节审校；文献逐条核验；未通过质量门禁的章节不得标记完成。
- **实验与代码**：书中需要用实验/代码说明的论断必须配可运行脚本；每幅仿真图由脚本生成并在 `figures/manifest.yaml` 登记；代码须通过冒烟测试、标注来源与许可。
- **资产合规**：公司实测数据（华为 NDA）引用前确认公开范围；IEEE/厂商图原创重绘；译稿在前言声明「编译/改写自」。

## 目录结构约定

- `docs/plan/`：策划与执行类文档（定位、提纲、实施计划、进度、评审、素材核验、知识资产、实验体系、文档规范、排版方案、资产台账）。
- `docs/chapters/`：各章正文（markdown），命名 `chNN-<slug>.md`，按实施计划第 3 节顺序推进。
- `docs/front/`：前言（含素材版权与引用说明）。
- `docs/appendices/`：附录 A–D 的 Markdown 源。
- `docs/templates/`：章节模板与 ElegantBook 4.7 排版模板。
- `book/`：排版工程（`main.tex`、`book.yaml`、`reference.bib`、生成的 `sections/`、构建产物 `build/`）；详见 [排版与构建方案](plan/typesetting.md)。
- `figures/`：各章图片，命名 `figures/chNN/figNN-MM-<slug>.{drawio,svg,png}`，每图附源文件；`figures/manifest.yaml` 为图-代码映射真源。
- `code/`：`hddbook/` 共享库、`experiments/` 章节实验、`tests/` 冒烟测试、`data/` 样例数据；详见 `code/README.md`。
- `tools/`：`md2tex.py`（Markdown→LaTeX）、`build_book.py`（构建 PDF）、`check_docs.py`（链接/manifest/台账检查）。

## 构建书籍 PDF

```bash
python3 tools/build_book.py      # 转换 Markdown 并构建 book/build/main.pdf
python3 tools/check_docs.py      # 一致性检查
```

环境要求：pandoc、TeX Live/MacTeX 2026（latexmk/xelatex/biber）。详见 [排版与构建方案](plan/typesetting.md)。
