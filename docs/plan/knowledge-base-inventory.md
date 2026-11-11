# 《深入浅出HDD》知识资产核验（2026-11-11）

> 核验人：kb-auditor（task-5）。数字均为本机实测（find/du/python 统计），未全量读取 References 文件内容；译稿结论沿用 `docs/plan/material-audit.md`，不重复核验。
> 优先级：P0=写正文即需、可直接取材/引用；P1=需筛选、转换或确认后使用；P2=备查/工具复用。

## 一、资产总览

| 资产 | 绝对路径 | 实测规模 | 内容概要 | 可用方式 | 章号 | 主要风险 | 优先级 |
|---|---|---|---|---|---|---|---|
| OpenKnowledgeBase | `/Volumes/Elements/OpenKnowledgeBase/OpenKnowledgeBase` | 21 GB；wiki 51,784 md（concepts 9,481/entities 32,132/sources 10,171）；References 17 GB/513,585 文件/223 集合；graph.json 366.6 MB；kb_index.json 33.3 MB | HDD/存储论文 wiki（Obsidian vault）+ MinerU 全文 + 知识图谱 + 检索索引 | 文献/理论/前沿/引用（kb search→paper→evidence→cite） | 3/5/7/16/18+全书文献 | README 规模表过期；MAMR tag 假命中；图版权 | P0 |
| References 论文库 | `/Volumes/Elements/References` | 53 GB；17,817 文件；11,426 PDF；222 个类别目录 | HDD/磁记录专题 PDF 库（HAMR/TDMR/BPMR/伺服/磁带/编码/会议 digest） | 文献、图源、综述 | 5/6/7/9/10/12/13/15/16/17 | IEEE 版权；命名混乱；与 OpenKB 重复 | P0 |
| IEEEtran 自著论文 | `/Volumes/Elements/IEEEtran` | 970 MB；431 PDF（含模板/校样）；18 个专题目录 | 作者论文与投稿材料（读信道建模、NN 检测、NLTS、TDMR/3DMR、蓝光） | 引用、图、实验结论、排版模板 | 5/6/7/12/16/17/18 | 含未发表稿件，需标注状态 | P0 |
| HDDGroup2025 | `/Volumes/Elements/HDDGroup2025` | 23 GB；26 个顶层条目 | HAMR 报告/Slides/实测数据/HAMR-Code-S1/S2/华为合同 | 实验、图、数据、仿真 | 15/16+附录C | 华为数据敏感；500Gb zip 全零 | P0 |
| HDDTapeGroup | `/Volumes/Elements/HDDTapeGroup` | 474 MB；1,110 文件 | 合同/SOW、PMR-TDMR 仿真软件说明、磁带报告、35 份月报 | 项目背景、理论、代码 | 2/5/6/7/16/17+附录C | 合同扫描件无文本层；公司保密 | P1 |
| TapeGroup2025 | `/Volumes/Elements/TapeGroup2025` | 7.2 GB；17 个顶层条目 | PRBS5 冲激响应数据、TDMR_RCP_MMSE、S1 报告、Slides、华为 TDMR 合同 | 数据、实验、报告 | 5/6/7/16/17+附录C | 华为 NDA/外发数据 | P0 |
| HAMR-Progress-20260423 | `/Volumes/Elements/HAMR-Progress-20260423` | 447 MB；Progress.md 338 行/17 KB；PDF 47 MB；assets 177 文件（127 png） | 读侧控制器 step1 servo-first/step2 write 参考检测进展 | 实验结论、图 | 15/16 | 内部报告；图片绝对路径失效 | P1 |
| HAMR-Progress-20260514 | `/Volumes/Elements/HAMR-Progress-20260514` | 13 MB；md 666 KB/203 行+15 png；PDF 6.5 MB | 双模式 servo+data 流水线、BER 与均衡收敛结论、改进计划 | 结论、图 | 15/16 | BER 口径不明；结论初稿 | P1 |
| DeepResearch | `/Volumes/Elements/DeepResearch` | 437 MB；local_kb 64 篇；kb_pipeline.py 3.8 KB；enhanced_knowledge_base.md 128 KB | OpenKB 前身：MinerU/OpenDataLoader/marker + LLM 增强管线 | 管线复用、单篇增强 | 16/18+附录C | 规模小；与 OpenKB 重复 | P2 |
| 译稿（7 套） | `/Volumes/Elements/HDD1-Volume-I`、`HDD2-Volume-II`、`HDD3-Volume-III`、`TranslationBooks/*/chinese_final` | 686,917 汉字/2,279 图（material-audit 实测）；images 实测 CSP 471/MECH 323/SERVO 239 文件 | Piya 三卷本、编码书 39 章、机电控制 5 章、伺服 11 章全文译稿 | 正文主干、理论素材 | 全书 | Piya/CRC/Springer 版权；公式 OCR；图需重绘 | P0 |

## 二、OpenKnowledgeBase 检索与取证路径（已实测可用）

```bash
cd /Volumes/Elements/OpenKnowledgeBase/OpenKnowledgeBase
python3 scripts/kb search "HAMR 二维检测" --limit 20 --json   # 返回 id/slug/concepts/collection/score
python3 scripts/kb paper "sources/<集合>/<页>.md" --json      # 结构化全文+Key Findings 校验
python3 scripts/kb evidence "<论断>" --json                  # 带出处的库内证据
python3 scripts/kb cite <id…> --format bibtex               # 生成引用
python3 scripts/kb vocabulary / compare <概念>              # 词表与跨论文指标对比
```

- 索引直查 `output/kb_index.json`（10,171 papers/36,163 concepts/39,244 authors；concept hamr 678、tdmr 446、bpmr 371、mamr 2,396（含 tag 假命中）、smr 406、nlts 107）。
- Obsidian：以 `wiki/` 为 vault，用 `Bases/Sources`、`By Collection`、`By Concept`、`By Year` 浏览；`wiki/Home.md` 为仪表盘（当前 10,171 sources/9,481 concepts/32,132 entities）。
- grep 检索：`grep -ril "关键词" wiki/sources wiki/concepts`；概念页按别名命名（无 HAMR.md，HAMR 见 3DHAMR/ThreeDimensionalHamr3DHamr 或走索引）。
- 图谱：`graph/graph.html` 用单页 Local graph；全局约 2.2 万结点，勿直接打开。
- 原文：`References/<集合>/<论文>.md`（MinerU md+图）；原始 PDF 在 `/Volumes/Elements/References/<类别>/`。
- 引用链：kb cite → bibtex；Zotero 同步 `scripts/sync_zotero.py`。
- 规模注意：OpenKB/References 有 513,585 文件，勿 grep 全库；优先 kb_index.json 与 wiki/sources 页。

## 三、References 论文库分类（HDD/磁记录相关，实测文件数/PDF数）

| 类别组 | 实测（文件/PDF） | 代表文献（1–2 篇） | 用途/章号 |
|---|---|---|---|
| 记录技术前沿 HAMR/TDMR/BPMR/3DMR-MAMR/PMR/IMR | 415/401（HAMR 140/134、TDMR 74/73、BPMR 64/62、3DMR-MAMR 108/103、PMR 13、IMR 16） | Kryder 2008 "Heat assisted magnetic recording"；Rottmayer 2006 "Heat-Assisted Magnetic Recording"；Khizroev 2004 "Three-Dimensional Magnetic Recording Device" | 第16章理论/文献/图源 |
| 会议 digest TMRC/APMRC/Intermag | 335/331（TMRC 156/155 含 TMRC2026 Digest；APMRC2018 80/79；Intermag 99/97 含 2024/2026） | TMRC_2026_Digest_Book；APMRC2018 Proceedings | 第16章最新进展 |
| 读信道 PRML-NPML/Readback Channel/Equalizer/Detector | 752/714 | Id 1996 "A Modified PRML Channel for PMR"；Victora 2025 "Vector Recording ... HAMR Read Head" | 第5/6/7/15章 |
| 模拟前端 ADC/Analog Front End | 31/29 | Uehara 1994 "100MHz Output Rate ADC for PRML Read Channels" | 第15章 |
| 定时恢复 Timing Recovery | 148/120 | Srinivasa 2015 "Timing Recovery Algorithms and Architectures for 2-D Magnetic Recording" | 第8/15章 |
| 伺服 Servo/Position Sensing | 209/166 | 伺服写入/PES/STW 论文 | 第9/10/11/15章 |
| 磁带 Tape | 378/357 | LTO/磁带记录与信道论文 | 第17章 |
| 编码 Constrained Codes/LDPC | 1,731（LDPC 1,479/298） | 多轨约束码、LDPC 存储应用论文 | 第12/13章 |
| 介质/噪声 Media/Noise | 45/44 | 介质噪声与颗粒噪声模型 | 第5章 |
| 存储系统会议 FMS/MSST | 678/675 | FMS 2025/2026、MSST | 第1/2/18章 |

> 说明：无独立 `IEEE Trans. Magn.` 目录，期刊论文分散在各专题目录；会议 digest 单独成库。命名中英混排，检索需同时试英文关键词与缩写。

## 四、IEEEtran 自著论文与投稿材料（与本书相关）

| 目录/文件 | 论文主题 | 状态 | 章号 |
|---|---|---|---|
| `APMRC2018/`（MAGCON-19-04-0016） | Read Channel Modeling and Neural Network Block Predictor for 2D Magnetic Recording | TMAG 2019 发表 | 5/7/16 |
| `TMAG-NLTS/`（TMAG-23-04-0212、TMAG3288371） | A Graded Precompensation Scheme by Pattern Classification on NLTS for PMR | TMAG 2023 发表（含终校） | 5 |
| `TMRC2019/` | A Study on Block-based NN Equalization in TDMR System with LDPC Coding | 会议全文+digest+poster | 7/12/16 |
| `Intermag2024/TMAG-AD03` | Decision-Feedback Single-Layer Read Reconstruction and Separation for 3D Magnetic Recording | Intermag digest | 16 |
| `Intermag2024/TMAG-AD11` | Quaternary Detection with NN Equalization for 3D Magnetic Recording | Intermag digest | 16 |
| `JMMM/`（MAGMA-D-24-01438） | On the impact of interlayer misalignment for dual-layer data detection in 3DMR | 期刊在审/返修 | 16 |
| `TMRC2025/` | Enhancing Bottom-Layer Detection in Dual-Layer 3D Magnetic Recording via Top-Layer-Assisted Signal Rescaling | 会议全文 | 16 |
| `CEEdc/`、`CEEsc/`、`AEUE-S-24-03350.pdf` | The Compatible Data Detection for Blu-ray Discs: From algorithm to implementation | 期刊投稿/在审 | 17 |
| `ECTI-CON2024/` | Partial Response and NN Equalized ML Detection for Blu-ray Discs | 会议 | 17 |
| `MDPI_Crystals_KL/` | A Graded Precompensation Scheme...（NLTS 期刊版） | 期刊 | 5 |
| `IEEEtran.cls`、`bare_jrnl_transmag.tex`、`bibtex/`、`中文期刊模板/`（47 PDF） | 排版与参考文献模板 | 可复用 | 附录/投稿 |

> 431 个 PDF 含模板/校样/重复版本；正式可引用论文约 10 篇，投稿状态需作者确认后再写入参考文献。

## 五、实验数据与报告资产（格式/可用性/敏感性）

| 路径 | 格式/规模 | 内容与结论 | 可用性/敏感性 | 章号 |
|---|---|---|---|---|
| `HDDGroup2025/HAMR-Code-S1` | Python 代码+`data/` npy/csv+`交付件/代码说明书.md`（2025-11-13） | coarse/medium/fine 粒度回读仿真、激光热辅助写入噪声、PRML 检测、BER 统计 | 可复现仿真；公司项目代码，可引用结论 | 5/6/7/16/附录C |
| `HDDGroup2025/1030-500Gb` | 17 个 CSV/Wfm CSV，1.8 GB | 500GB HDD 9 sectors 读/写原始波形（含 2GHz 低通版）、30TB HAMR 写入信号 | 实测波形可作图；华为数据，发布前确认 | 5/15 |
| `HDDGroup2025/write+read-800000001+255-test1` | Wfm.bin 776 MB + bin 16 KB | 示波器原始读写波形 | 原始数据；同上 | 15 |
| `HDDGroup2025/500gHDD-*.zip` | read 3.32 GB + write 1.20 GB | 实测全部字节为 0（非 zip 结构），不可用 | 改用 1030-500Gb/RAR | — |
| `HDDGroup2025/HAMR-Report-S1` | main.pdf 58 页、186 图、LaTeX 分章 | HAMR 回读模型（粗/中/细粒度）、均衡器、检测器、一阶段实验结果 | 技术报告，可引结论/重绘图；内部 | 5/6/7/16 |
| `HDDGroup2025/Slides` | 19 组 2025-08–2026-05 汇报 | 周/月报，结论线索与示意图 | 仅作线索；内部 | 15/16 |
| `TapeGroup2025/20260114_PRBS5…` | 2.7 MB；ch0–7 十进制回读 125 MSaps；冲激响应 CSV 32 行 | 磁带 4.66 m/s、46.6 nm 比特长、2.85 µm 道宽、0.8 µm 读头；DSS 12T+VFO 2T+PRBS5 100 Mbps | 实测冲激响应/dibit，可作第5章图与数据；外发文件，NDA | 5 |
| `TapeGroup2025/TDMR_RCP_MMSE` | 33 个 .m + results（d20260331-174112、SNR28） | 2D GPR/RCP MMSE 均衡与 MLSE 仿真 | 可复现仿真；华为 TDMR 项目 | 6/7/16/附录C |
| `TapeGroup2025/S1` | 7 个 PDF | PRML-dynamicNLTS 仿真、TDMR RCP MMSE 报告、dibit 理论/手册、磁传递函数、MR 趋势 | 报告可引结论；内部 | 5/6/7/17 |
| `TapeGroup2025/Report`（2,084 文件） | md+PDF+bib+drawio | 报告_20260523：HAMR/TDMR/MLMR/VR 四份研究报告；磁传递函数技术报告（互易原理/屏蔽读头/粗细粒度/失真） | 综述素材与图；内部 | 5/16/17 |
| `HAMR-Progress-20260423` | md 338 行+PDF 47 MB+assets 177 文件 | step1 42 spokes/41 gaps/70 段 timing 全部有效；step2 DSM 识别与 VA 检测 | 实验结论/图；内部；md 图片路径需修正 | 15/16 |
| `HAMR-Progress-20260514` | md 203 行+15 png+PDF 6.5 MB | 双模式流水线实现；部分段 EQ 误差收敛但整体发散；最优段 BER 0.35（口径待确认）；改进为 EQ 前 TR 后 | 结论/图；初稿 | 15/16 |
| `HDDTapeGroup` 合同/SOW | PDF/DOCX/XLSX | SOW1215 指标：PMR+TDMR>1.33 Tb/in²、HAMR+TDMR 5–7 Tb/in²、译码后 BER<1e-15；委托开发合同 8 页扫描件 | 项目背景/工程指标；公司保密 | 2/16 |
| `HDDTapeGroup/TapeReport`、`main-R1-20230728.pdf` | 79 文件；报告 39 页 | TapeTech.md 磁带技术研究报告；磁带算法设计与仿真报告（2022/9–2023/1） | 第17章素材；内部 | 17 |
| `HDDTapeGroup/RegularReports` | 35 份月报（2021-11–2025-06） | HDD 合作交流反馈与阶段汇报 | 仅作线索；公司保密 | 2 |

## 六、结论：使用建议与风险

1. **最有价值 5 类（按可立即取材排序）**：① OpenKB wiki+kb_index（第16/18章文献与前沿，kb 检索链完整）；② References 的 HAMR/TDMR/BPMR/TMRC/Intermag 子库（415+335 篇，含 TMRC2026）；③ IEEEtran 自著 10 篇（第5/7/16/17章可正式引用并重绘图）；④ HDDGroup2025 HAMR-Code-S1+1030-500Gb 实测（第15/16章实验与数据）；⑤ TapeGroup2025 PRBS5+磁传递函数/PRML-dynamicNLTS/TDMR_RCP_MMSE（第5/6/7章实测与仿真）。
2. **数据敏感性**：HDDGroup2025（华为 HAMR SOW：620 Gb/in² PMR、1575 Gb/in² 30T HAMR、2.6 Tb/in² 挑战 4 Tb/in²）、TapeGroup2025（华为 TDMR TC20251106007，含 NDA 保密承诺书）、HDDTapeGroup（HDD 原型算法合同）均为公司横向项目；原始波形与内部报告引用前需确认，图建议重绘或标注“本实验室实测”。
3. **版权**：References/IEEE 论文只可引用不可整图复制；OpenKB wiki 是 MinerU+LLM 摘要页，引用须回溯原文并标 DOI；译稿版权在 Piya/CRC/Springer（material-audit 第五节），厂商/IEEE 图按前言计划原创重绘。
4. **时效**：TMRC2026 Digest、Intermag2026、2026 年 HAMR 进展报告最新；References 以 1990s–2010s 为主，第16/18章需补 2024–2026 文献（kb search 可按年过滤）。
5. **一致性**：OpenKB README 规模表（11,542/4,869/5,729）与 Home.md 及实测（10,171/32,132/9,481）不一致，引用规模用 Home.md 或实测；kb_index.json 建于 2026-11-01。
6. **检索坑**：MAMR 因全局 tag `3dmr-mamr` 假命中（索引 2,396 vs 大小写敏感约 351）；wiki/concepts 无 HAMR.md，需别名/索引；graph.json 366 MB 勿直接打开；OpenKB/References 513,585 文件勿全库 grep。
7. **数据坑**：500gHDD-readdata/writedata zip 全零（3.32 GB/1.20 GB），有效数据在 1030-500Gb（17 CSV）与 RAR；HAMR-Progress-20260423 的 md 图片指向旧目录 `/Volumes/Elements/HAMR-Progress/assets`，需改为 `HAMR-Progress-20260423/assets`。
8. **格式**：实测数据为示波器 CSV/Wfm CSV/bin/npy/十进制 txt；仿真为 MATLAB（TDMR_RCP_MMSE、HDDTapeGroup/TDMR）与 Python（HAMR-Code-S1/S2）双栈，附录 C 需统一 Python 并给数据读取脚本。
9. **可引用性分层**：IEEE/TMRC/Intermag 论文与 digest 可正式引用；SOW 指标可作“项目背景/工程指标”；月报、内部 Slides、进展报告只作线索或标注“内部资料”。
10. **缺口与下一步**：第18章无译稿落点，用 OpenKB 2024–2026 论文+项目结论原创；第9章“驱动放大”仍缺专节。建议先建 `references.bib`（kb cite + IEEEtran bibtex），再从 HAMR-Code-S1/PRBS5/TDMR_RCP_MMSE 提取 3–5 个可复现实验进附录 C，最后完成华为/NDA 数据引用确认清单。
