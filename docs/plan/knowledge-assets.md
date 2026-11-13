# 《深入浅出HDD》知识资产总图（V1.0 · 2026-11-11）

> 目的：把**书籍翻译、知识库、论文库、实验项目、项目报告与实测数据**理成一张可执行的资产地图——每类资产支撑哪些章、以什么方式使用、有什么风险、优先级如何。
> 关联：[素材核验](material-audit.md) · [实验资产清单](experiment-inventory.md) · [知识库核验](knowledge-base-inventory.md) · [实验与代码体系](experiments.md) · [文档与资产管理规范](document-management.md) · [资产台账](asset-registry.csv)

---

## 一、资产分类与总量（实测）

| 类别 | 资产 | 规模 | 对本书的价值 | 优先级 |
|------|------|------|--------------|--------|
| 书籍译稿 | Piya 三卷本、编码与信号处理、HDD 机电控制、伺服系统、Rice 数字通信（8 套） | 88.0 万汉字（其中 Rice 译本 19.3 万汉字、2,813 图）、5,092 图 | 全书理论主干与章节骨架（全文翻译，需裁剪/改写；Rice 译本须按勘误协议使用） | P0 |
| 知识库 | OpenKnowledgeBase（wiki + kb_index + graph + References） | 21 GB；10,171 篇论文、9,481 概念、32,132 实体 | 第 16/18 章前沿、全书文献与证据链 | P0 |
| 论文库 | /Volumes/Elements/References | 53 GB；11,426 PDF、222 类别 | 文献、图源、综述；HAMR/TDMR/BPMR/TMRC 等 | P0 |
| 自著论文 | /Volumes/Elements/IEEEtran | 431 PDF；可正式引用约 10 篇 | 第 5/7/16/17 章的一手结论与图 | P0 |
| 实验项目 | 16 项（RSI4HDD、PRML-Explore、PSP、HamrSimulator、RLL、TDMR_RCP_MMSE、pytdmr、dibit 等） | 8 项可运行 Python、6 项带测试/对拍 | 附录 C 12 个核心实验与章节演示 | P0 |
| 项目报告 | HDDGroup2025、TapeGroup2025、HDDTapeGroup、HAMR-Progress×2 | 报告/Slides/月报/代码说明书 | 第 2/5/6/7/15/16/17 章工程结论 | P1 |
| 实测数据 | 1030-500Gb（17 CSV/1.8 GB）、PRBS5 冲激响应、HAMR 写入波形 | 实测波形与冲激响应 | 第 5/15/16 章校准与图 | P0（需 NDA 确认） |
| 工具/模板 | IEEEtran 模板、bibtex、drawio、MinerU/OpenKB 管线 | 可复用 | 排版、引用、图件、知识抽取 | P2 |

> 完整清单见[知识库核验](knowledge-base-inventory.md)与[实验资产清单](experiment-inventory.md)；逐条台账见 `asset-registry.csv`。

---

## 二、使用原则（三条铁律）

1. **三源交叉**：每个关键技术论断至少有两个独立来源（译稿/教材 + 论文/实测数据），公式须独立推导或仿真验证；单一来源的结论标 `[待核]`。
2. **分层使用**：理论素材（译稿）→ 改写为教学叙述；文献（OpenKB/References）→ 支撑与引用；实验（代码项目）→ 生成图与验证；数据（实测）→ 校准与案例。**禁止把译稿当论文引用，禁止把内部报告当公开文献引用**。
3. **合规先行**：公司数据（华为 NDA）先确认公开范围；IEEE/厂商图重绘；译稿在前言声明「编译/改写自」；自著未发表论文标注状态。

---

## 三、章节-资产映射矩阵

> 每章给出：理论主源（译稿）、文献/前沿源、实验/数据源、引用策略。实验 ID 见[实验与代码体系](experiments.md)第三节。

| 章 | 理论主源（译稿） | 文献/前沿源 | 实验/数据源 | 引用策略 |
|----|------------------|-------------|-------------|----------|
| 1 简介 | CSP1、CSP 前言 | FMS/MSST、IDC 报告 | 无实验；项目 SOW 指标 | 产业数据须标年份与来源 |
| 2 数据存储 | CSP1/CSP3、V1ch1 | FMS/MSST、References 存储系统 | 合同指标（PMR/TDMR/HAMR） | 厂商数据标白皮书版本 |
| 3 磁记录基础/材料工艺 | V1ch1、CSP4/14/16 | OpenKB 概念（WriteHead/ReadHead/Media）、References 介质/磁头 | 无实验；参数表 | 厂商图重绘 |
| 4 数学工具 | V1ch2–5、CSP7 | 教材（Bertram 等） | 无实验；附录 A | 经典教材引用 |
| 5 记录物理/信道 | CSP2/5/6、V1ch6 | References 读信道/介质噪声；IEEEtran NLTS 论文 | exp:5-1~5-5；PRBS5 实测冲激；dibit | 实测数据标「本实验室实测」 |
| 6 均衡 | CSP8、V2ch3、V1ch5.6 | References 均衡/PRML；IEEEtran NN 均衡 | exp:6-1~6-3；PRML-Explore、TDMR_RCP_MMSE、ABCForDisc | 算法引用原始论文 |
| 7 检测 | CSP32/33、V2ch4–7、V3ch3 | References 检测/PRML；IEEEtran NN 检测 | exp:7-1~7-3；PRML-Explore、RSI4HDD、pytdmr | 对拍结果作验证 |
| 8 定时 | V2ch2、CSP26/27、**Rice Ch8 + 附录 C**（需勘误，见 [定时恢复资产包](assets-timing-recovery.md)） | References 定时恢复；PSP docs 论文；Kovintavewat 2003/2012 | exp:8-1~8-2；PSP、RSI4HDD timing、MATLAB symbol_timing_sync（对拍） | 引用 ITR/OPSP 原始论文；Rice 书按原书页码引用 |
| 9 伺服机构 | MECH2/3、SERVO2–7 | References 伺服/PES/STW | exp:9-1~9-2（新写 servo） | 机电控制教材 + 论文 |
| 10 主轴/STW | MECH4/5 | References 伺服写入 | exp:10-1~10-2（新写） | 工程参数标来源 |
| 11 双级执行器 | SERVO8–11 | References 双级/微驱动 | exp:11-1（新写） | 基准问题引用原文 |
| 12 ECC | CSP9、V3ch2–4、CSP35–38 | References LDPC/约束码；IEEEtran TDMR-LDPC | exp:12-1~12-2；pytdmr | 码率/性能标仿真条件 |
| 13 RLL | V2ch8、CSP11/17–21 | References 约束码；专利 US6241778 等 | exp:13-1~13-2；RLL 库、HamrSimulator 码表 | 专利号必须标注 |
| 14 信息论 | CSP12/13/23 | References 容量/可达速率 | exp:14-1（新写 capacity） | 容量数值标信道模型 |
| 15 通道/伺服信号 | CSP15/16/29/30/34、V2ch1 | References 读信道/伺服信号；HAMR 进展报告 | exp:15-1~15-2；PRMLpro、PSP、SYNCDEMO 数据、1030-500Gb | 内部报告标「内部资料」 |
| 16 热凸点/前沿 | CSP31/24/25/39、V3ch6–8 | OpenKB 2024–2026；References HAMR/TDMR/BPMR/TMRC2026；IEEEtran 3DMR | exp:16-1~16-4；HamrSimulator、TDMR、ABCForDisc、HAMR-Code-S1 | 前沿结论须 2024–2026 文献 |
| 17 其他存储 | CSP3、磁带/光盘译稿 | References Tape/Optical；HDDTapeGroup 报告 | exp:17-1~17-2；BD_Sim | 标准号（BD/ISO）标注 |
| 18 展望 | 无译稿落点 | OpenKB 2024–2026、FMS/MSST、IEEEtran | 无实验；项目结论 | 预测性结论标「作者判断」 |

---

## 四、各类资产的使用规程

### 4.1 译稿（理论素材）
- 入口：`material-audit.md` 查每章素材充足度与倍率；按「过剩章裁剪、偏薄章扩写」执行。
- 使用：改写为教学叙述，禁止整段照搬；公式清洗 OCR 伪影后复核；图全部重绘。
- 版权：Piya/CRC Press/Springer；前言声明「编译/改写自」，二手译稿不作学术引用。
- **Rice 数字通信译本（TR-07）特别规程**：公式与 `\tag` 逐字节保留（Ch8 138/138、附录 C 70/70），但正文措辞、术语与脚注编号有残留错误；使用前按 [定时恢复资产包](assets-timing-recovery.md) 第三节做三源交叉，并在 [勘误登记](errata-digital-communications.md) 逐条留痕。该译本为 CC BY-NC-ND 4.0，不得整段照搬。

### 4.2 OpenKnowledgeBase（文献与证据）
```bash
cd /Volumes/Elements/OpenKnowledgeBase/OpenKnowledgeBase
python3 scripts/kb search "<主题>" --limit 20 --json
python3 scripts/kb paper "<sources/集合/页.md>" --json
python3 scripts/kb evidence "<论断>" --json
python3 scripts/kb cite <id> --format bibtex
```
- 用于第 16/18 章前沿与全书文献；`kb_index.json`（10,171 papers）优先，勿全库 grep（513,585 文件）。
- 引用必须回溯原文并核 DOI；MAMR 有 tag 假命中（2,396 vs ~351），概念页无 HAMR.md，用别名/索引。

### 4.3 References 论文库
- 按类别取 PDF：HAMR 140、TDMR 74、BPMR 64、3DMR-MAMR 108、TMRC 156（含 2026）、Intermag 99、读信道 752、编码 1,731。
- 只引用不整图复制；图重绘；命名混乱，检索同时试英文与缩写。

### 4.4 IEEEtran 自著论文
- 可正式引用约 10 篇（TMAG 2019/2023、TMRC2019/2025、Intermag AD03/AD11、JMMM 在审、BD 检测投稿）。
- 未发表/在审稿件必须标注状态；图可重绘使用。

### 4.5 实验项目
- 入口：`experiment-inventory.md`（16 项事实与移植评估）；执行：`experiments.md`（分级、矩阵、验收）。
- 优先移植带测试的 8 项；MATLAB 主链只作参考；代码入仓前完成许可确认。

### 4.6 项目报告与实测数据
- HDDGroup2025：HAMR-Code-S1（Python 仿真）、1030-500Gb（17 CSV 实测）；500gHDD zip 全零不可用。
- TapeGroup2025：PRBS5 冲激响应（125 MSaps、46.6 nm）、TDMR_RCP_MMSE、磁传递函数报告。
- HDDTapeGroup：SOW 指标（PMR+TDMR>1.33 Tb/in²、HAMR+TDMR 5–7 Tb/in²、BER<1e-15）可作工程背景。
- HAMR-Progress×2：step1/step2 结论与图；图片路径需修正。
- **合规**：华为横向项目（NDA），原始波形与内部报告引用前确认；图建议重绘或标「本实验室实测」。

---

## 五、交叉核验与引用链

1. **论断→证据**：正文关键结论建立「论断 ID → 译稿小节 / 论文 DOI / 实验 ID / 实测数据」四列对照，写入章节素材包。
2. **引用链**：`references.bib`（kb cite + IEEEtran bibtex）为唯一文献库；正文引用编号由 bib 生成；每条 DOI/ISBN 核验。
3. **数据口径**：任何 BER/SNR 结果必须同时声明 SNR 定义、α、OSR、码率、目标响应；实测数据声明采样率、带宽、比特长、道宽。
4. **图文一致**：图由 `code/experiments/` 生成，manifest 登记；禁止手工改图。
5. **时效**：第 16/18 章以 2024–2026 文献为主（TMRC2026、Intermag2026、HAMR 进展）；经典理论用原始文献。

---

## 六、风险与合规清单

| 风险 | 涉及资产 | 处置 |
|------|----------|------|
| 华为 NDA 数据 | HDDGroup2025、TapeGroup2025、HDDTapeGroup | 建立「可公开/需确认/不可公开」清单；图重绘或标「本实验室实测」 |
| IEEE/厂商图版权 | References、IEEEtran、译稿图 | 全部重绘；图 license 台账；必要时申请 permission |
| 译稿版权 | 8 套译稿（含 Rice CC BY-NC-ND 4.0） | 前言声明；改写不照搬；不作学术引用；Rice 译本另建勘误登记 |
| 知识库数字过期 | OpenKB README | 用 Home.md/实测数字；引用规模注明日期 |
| 数据无效 | 500gHDD zip 全零 | 改用 1030-500Gb/RAR；入库前校验 SHA256 |
| 概念假命中 | MAMR tag | 用大小写敏感检索 + 人工核对 |
| 未发表论文 | IEEEtran 在审稿 | 标注「在审/预印本」，不冒充已发表 |
| 公式 OCR 伪影 | 译稿 | 清洗后复核；符号统一到附录 B |

---

## 七、优先级与下一步（可执行）

**P0（本周）**
1. 建 `references.bib`：用 `kb cite` + IEEEtran bibtex 导入第 5/7/16 章核心文献（≥40 条），逐条核 DOI。
2. 建 `docs/plan/asset-registry.csv` 并补全 8 类资产与 16 个实验项目的条目（本文件已建初始版）。
3. 出「华为/NDA 数据引用确认清单」：列出拟使用的图/数据/结论，交作者确认公开范围。
4. 校验实测数据：1030-500Gb CSV 可读性、PRBS5 冲激响应完整性；剔除全零 zip。
5. 第 5 章素材包：按矩阵取 CSP2/5/6、V1ch6、PRBS5、dibit，标注每条论断的证据来源。
6. 第 8 章素材包：Rice Ch8 + 附录 C（按勘误协议）、MATLAB `symbol_timing_sync` 对拍值、PSP 的 ITR/OPSP 代码与论文；先登记 V-01~V-06 待核项。

**P1（两周内）**
6. OpenKB 检索 SOP 固化：主题→论文→证据→bibtex→DOI 核验，写入 `docs/plan/kb-sop.md`。
7. 确认 IEEEtran 10 篇论文的发表/在审状态，更新引用。
8. 补 2024–2026 前沿文献（TMRC2026、Intermag2026、HAMR 进展）。

**P2（随章）**
9. 每章素材包附「资产使用记录」（用了哪些译稿小节/论文/实验/数据）。
10. 季度更新资产台账与知识库规模数字。
