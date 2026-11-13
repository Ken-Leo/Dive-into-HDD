# 定时恢复（Timing Recovery）资产包：来源、勘误协议与章节映射

> 建立日期 2026-11-13｜用途：为第 8 章「时钟/定时恢复」与第 15 章「数据存取通道与伺服信号处理」建立可追溯的理论源、参考实现与勘误流程。
> 关联：[知识资产总图](knowledge-assets.md) · [实验资产清单](experiment-inventory.md) · [资产台账](asset-registry.csv) · [第 5 章样章](ch05-outline.md) · [实施计划](implementation-plan.md)

---

## 一、资产清单（三套，均为本机现存）

| 编号 | 资产 | 路径 | 规模 | 许可/版权 | 在书中的角色 |
|------|------|------|------|-----------|--------------|
| TR-07 | Michael Rice《Digital Communications: A Discrete-Time Approach》中英对照译稿（801 页原书；10 章 + 附录 A–C） | `/Volumes/Elements/TranslationBooks/digital_communications` | 244 MB；15 个中英 Markdown、1,370 处图引用、`book_clean.pdf` | 原书 © Michael Rice；译本 CC BY-NC-ND 4.0（翻译模型 Qwen3.8-Flash-Next） | 第 8 章理论主源（Ch8 + 附录 C）；第 5/7 章信道与检测的补充参考 |
| EXP-17 | symbol_timing_sync（MATLAB 定时恢复仿真器，基于 Rice 第 8 章） | `/Users/kenleo/Documents/References/Timing Recovery/PLL/symbol_timing_sync-master` | 440 KB；11 个 `.m` + 1 个 `.mlx` | 无 LICENSE 文件（未声明）；依赖 MATLAB Communications Toolbox | 第 8 章算法参考与数值对拍（S 曲线、TED 增益、环路常数） |
| EXP-10 | PSP（OPSP-VA + ITR 2012 磁记录定时恢复） | `/Volumes/Elements/PSP` | 229 MB；Python 源码 + 81 项 pytest + 31 篇 docs（含 2 篇原始论文 PDF） | Apache-2.0；git 作者 kenleo | 第 8/15 章实验主代码；附录 C 定时恢复实验 |

**核验状态**：PSP 用系统 Python 采集到 81 项测试，`test_ted.py/test_pll.py/test_signal_gen.py` 子集 28 项全部通过（0.09 s）；PSP 自带 `.venv` 缺 pytest，直接跑 `.venv/bin/python -m pytest` 会失败，须用系统 `python3` 或重装 venv。MATLAB 仓库未在本机跑通（无 MATLAB 运行环境记录），按「参考实现 + 数值对拍」使用。

---

## 二、Rice 书第 8 章与附录 C 的结构（可直接作为第 8 章骨架）

原书第 8 章「Symbol Timing Synchronization」页码 436–515，节次如下：

| 节 | 标题（英/中） | 页码 | 对本节的用途 |
|----|---------------|------|--------------|
| 8.1 | Basic Problem Formulation / 基本问题描述 | 436 | 定时误差对眼图与信号空间投影的影响；PLL 三要素（TED/环路滤波/VCC） |
| 8.2 | Continuous-Time Techniques for M-ary PAM | 438 | 连续时间 MLTED、早-晚门、过零检测；S 曲线与自噪声 |
| 8.3 | Continuous-Time Techniques for MQAM | 443 | 正交两路联合误差信号；QPSK 早-晚门 |
| 8.4 | Discrete-Time Techniques for M-ary PAM | 445 | **本章主体**：8.4.1 TED（MLTED/ELTED/ZCTED/GTED/MMTED）、8.4.2 插值、8.4.3 插值控制（NCO/模 1 计数器）、8.4.4 环路滤波器与常数、8.4.5 性能 |
| 8.5 | Discrete-Time Techniques for MQAM | 494 | 复数基带与两路定时 |
| 8.6 | Discrete-Time Techniques for Offset QPSK | 497 | 偏移 QPSK 的定时特殊性 |
| 8.7 | Dealing with Transition Density / 处理跃变密度 | 501 | 自噪声与数据跃变密度的关系；MAN 脉冲形状；扰码/随机化（IRIG-106） |
| 8.8 | Maximum Likelihood Estimation / 最大似然估计 | 503 | MLTED 的似然推导；定时偏移估计上界 |
| 8.9 | Notes and References | 513 | 文献溯源（含 Gardner、Mueller-Müller 原始文献） |
| 8.10 | Exercises | 515 | 习题参考（可改造为 HDD 语境习题） |

附录 C「Phase Locked Loops」页码约 604–640：C.1 连续时间 PLL（C.1.1 输入、C.1.2 相位误差与环路滤波器、C.1.3 瞬态分析、C.1.4 带宽、C.1.5 捕获、C.1.6 跟踪、C.1.7 环路常数选择）、C.2 离散时间 PLL（含 C.2.1 示例）、C.3 注释、C.4 习题。**第 8 章的环路设计与稳定性论证应以附录 C 为准，并自行复核公式。**

---

## 三、勘误协议（强制，使用该书前必须执行）

用户明确要求：**该书部分内容需勘误，使用时务必检查**。据此建立四步协议，任何从该书进入书稿的内容都必须留痕：

1. **三源交叉**：每条拟用论断至少核对两个来源——① `source_final/` 英文原文；② `book_clean.pdf` 原书对应页；③ MATLAB 参考实现（`symbol_timing_sync`）或 PSP 的 Python 实现。三者不一致时以「原书 + 可运行代码」为准，译本仅作阅读辅助。
2. **公式重排**：译本公式为 MinerU 抽取，`\tag{}` 与符号逐字节保留，但**空格被拆散**（如 `N = 3 2`、`0 . 2 3 5`），且脚注编号会粘进正文数字（见 E-01）。进入书稿前必须重排为规范 LaTeX，并与原书公式编号核对。
3. **术语统一**：译本术语与本书既定术语不一致处，按第五节映射表改写；不得直接沿用译本措辞。
4. **登记**：每条发现写入 `docs/plan/errata-digital-communications.md`（新建），字段为 `ID / 位置(章.节.式号/页) / 原文 / 问题类型 / 更正 / 证据(源文件行号或代码行) / 状态`。未登记的引用视为未核验。

### 3.1 已登记勘误（首次核验，2026-11-13）

| ID | 位置 | 问题 | 更正 | 证据 |
|----|------|------|------|------|
| E-01 | 8.7 节首段 | 脚注编号「4」粘入正文，译本作「跃变密度约为4 50%」 | 应为「约为 50%（脚注 4）」 | `source_final/chapter_8.md` 原文 `approximately4 50%`；`chinese_final/chapter_8.md` 第 2964 行 |
| E-02 | 8.4.1 正文与图 8.4.4/8.4.7/8.4.11 题注 | 同一量 $K_p$ 被译作「检测器增益」与「鉴相器增益」两种；源书亦混用 `detector gain` / `phase detector gain` | 本书统一为「TED 增益 $K_p$（等效鉴相增益）」，首次出现处定义 | `source_final/chapter_8.md` L497 vs L520/L678/L932；`chinese_final/chapter_8.md` L497 vs L520 |
| E-03 | 全章 | `transition`/`transition density` 译作「跃变/跃变密度」，与本书第 5 章既定「翻转/翻转密度」不一致 | 统一改为「翻转/翻转密度」；首次出现处标注英文 | 第 5 章正文与 `ch05-outline.md` 用「翻转」 |
| E-04 | 图题注与参考文献 | 参考文献编号被 PDF 抽取拆散（如「[ 1 4 1 ]」），图题注中的数字亦有空格残留 | 引用时按原书页码核对；书稿中重排编号 | `chinese_final/chapter_8.md` 图 8.7.2 题注 |
| E-05 | 8.1 节 | `NCO` 保留英文缩写未在首次出现处定义 | 首次出现写「数控振荡器（NCO）」 | 译本 8.1/8.4.2 |
| E-06 | 全章公式 | 公式与 `\tag` 逐字节保留（第 8 章 138 个 tag、附录 C 70 个 tag 与英文源完全一致），但空格拆散、上下标可能丢失 | 公式可用，但必须重排并逐式核对原书 | 自动核验：tag 集合完全相同，行内公式 988/988、行间公式 192/192 |

### 3.2 自动核验结论（2026-11-13）

- 第 8 章：源/译 `\tag` 数量 138/138、集合完全一致；行内公式 988/988、行间公式 192/192；标题 19/19 一一对应。
- 附录 C：`\tag` 70/70；行内公式 459/459、行间公式 84/84；标题 15/15。
- 数字 token 差异仅来自公式编号（8.19/8.21/8.25/8.106 等）与脚注标记，未见数值语义漂移。
- **结论**：译本的结构与公式可信，风险集中在**正文措辞、术语与脚注残留**；按第三节协议处理后可用于写作，但不得整段照搬。

---

## 四、术语映射表（源书 → 本书，写作时强制）

| 英文 | 译本用词 | 本书用词 | 说明 |
|------|----------|----------|------|
| transition / transition density | 跃变 / 跃变密度 | 翻转 / 翻转密度 | 与第 5 章、第 13 章 RLL 术语一致 |
| timing error detector (TED) | 定时误差检测器 | 定时误差检测器（TED） | 首次出现给英文缩写 |
| phase detector gain / detector gain $K_p$ | 鉴相器增益 / 检测器增益 | TED 增益 $K_p$ | 统一，见 E-02 |
| S-curve | S 曲线 | S 曲线（鉴相特性） | 首次出现说明物理含义 |
| excess bandwidth | 超额带宽 | 超额带宽（滚降系数 α） | 与第 5/6 章滚降参数对应 |
| interpolator / interpolation control | 插值器 / 插值控制 | 插值器 / 插值控制（NCO） | 与第 15 章 ITR 对应 |
| voltage controlled clock (VCC) | 压控时钟 | 压控时钟（VCC） | 连续时间实现，HDD 中少见 |
| NCO / DDS | 未定义缩写 | 数控振荡器（NCO） | 见 E-05 |
| self-noise | 自噪声 | 自噪声 | 与数据图样相关，需结合 5.5.3 非线性 |
| transition density | 跃变密度 | 翻转密度 | 与第 5 章噪声谱、第 13 章 RLL 衔接 |

---

## 五、MATLAB 参考实现映射（`symbol_timing_sync-master`）

| 文件 | 功能 | 对应节 | 用途 |
|------|------|--------|------|
| `main.m` | 端到端仿真：脉冲成形 PAM/QAM + AWGN + 定时恢复环 | 8.4 | 参数模板（L、M、N、Bn·Ts、ζ、rolloff、TED、intpl） |
| `symbolTimingSync.m` | TED + 插值器 + 控制器 + PI 环路 | 8.4.1–8.4.4 | 环路结构参考；逐块对照 |
| `calcSCurve.m` / `simSCurve.m` | 解析/仿真 S 曲线 | 8.4.1 | 与书中 S 曲线图对拍 |
| `calcTedKp.m` / `plotTedGain.m` | TED 增益 $K_p$ 与滚降关系 | 8.4.1/8.4.4 | 环路常数设计输入 |
| `piLoopConstants.m` | PI 环路常数（由 $B_nT_s$、ζ、$K_p$ 计算） | 附录 C.2 | 与 C.61 式对拍 |
| `polyInterpFilt.m` / `polyDecomp.m` | 多相插值器设计与分解 | 8.4.2 | 插值器实现细节 |
| `derivativeMf.m` | 微分匹配滤波器 | 8.4.1 | MLTED 实现 |
| `genTestVector.m` | 输入/输出测试向量 | — | 对拍数据 |

支持的 TED：MLTED、ELTED、ZCTED、GTED、MMTED；插值器：多相、线性、二次、三次。`experiments.md` 记录的关键结论（可直接引用并需复核）：低过采样（L=2）+ 采样时钟频偏下，线性插值性能显著劣化；二次插值改善但仍有周期性星座畸变；三次与多相插值可消除；该现象在 L=8 时消失。**这条结论可作为第 8 章「插值阶数与 OSR 的折中」的工程要点，但须用 PSP 的 Python 实现独立复现后才可写入书稿。**

---

## 六、PSP 项目映射（`/Volumes/Elements/PSP`，Apache-2.0）

| 模块 | 内容 | 对应章/节 |
|------|------|-----------|
| `src/channel/` | PMR/LMR dibit 响应、介质抖动 $\sigma_j/T$、时钟抖动 $\sigma_w/T$、频偏 | 第 5 章 5.3/5.4；第 8 章实验信道 |
| `src/frontend/fse.py` | 分数间隔均衡（Wiener/LMS/NLMS） | 第 6 章；第 8 章定时环前端 |
| `src/opsps_va/` | 逐幸存路径 PLL（每路径独立 τ、θ）+ Viterbi + GPR trellis + TED（Early-Late/MM） | 第 7/8 章；第 15 章 |
| `experiments/itr_2012/` | ITR 2012 参考系统：Farrow 插值、NCO、二阶环路、MM TED | 第 8 章主体实验 |
| `docs/` | 31 篇工作记录 + Kovintavewat 2003/2012 原始论文 PDF | 引用源（ITR/OPSP 原始文献） |
| `tests/` | 81 项 pytest（`test_ted.py`、`test_pll.py`、`test_viterbi_slicer.py` 等） | 实验可复现性依据 |
| `data/` | 固定 seed 的 BER CSV（N1/N2、PW2.5、PMR） | 第 8 章 BER 曲线数据源 |

**使用方式**：优先移植 `experiments/itr_2012/` 与 `src/opsps_va/` 到 `code/experiments/ch08_*.py`（保留 Apache-2.0 声明与作者署名）；`docs/` 中的论文 PDF 用于引用，不整图复制。

---

## 七、第 8 章骨架草案（基于 Rice 8.1–8.10，HDD 语境改写）

目标 20 页 / 1.3 万汉字 / 14 图 / exp:8-1~8-2（见[实施计划](implementation-plan.md)）。草案：

| 节 | 标题 | 理论来源 | 实验/图 |
|----|------|----------|---------|
| 8.1 | 定时恢复在 HDD 中的位置：伺服段前导、数据段 PLL 与 ITR | Rice 8.1；第 5 章信道 | 图：定时误差对眼图与 BER 的影响 |
| 8.2 | 定时误差检测：MLTED/ELTED/ZCTED/GTED/MMTED 的统一框架 | Rice 8.2/8.4.1 | 图：五类 TED 的 S 曲线族；exp:8-1 |
| 8.3 | S 曲线、TED 增益与环路常数设计 | Rice 8.4.1/8.4.4 + 附录 C | 图：$K_p$–滚降曲线；表：环路常数 |
| 8.4 | 插值与插值控制：Farrow/多相/线性二次三次 | Rice 8.4.2/8.4.3 | 图：插值阶数与 MER 关系 |
| 8.5 | 数据图样与自噪声：翻转密度、扰码与写前补偿的耦合 | Rice 8.7 + 第 5 章 5.5.3 | 图：翻转密度–TED 增益 |
| 8.6 | 频率偏移与捕获：二阶环路、频偏估计、失锁检测 | 附录 C.2 + PSP ITR | 图：频偏捕获轨迹 |
| 8.7 | ITR 与逐幸存路径定时（OPSP）：HDD 特有的联合检测 | PSP OPSP-VA/ITR 2012 | exp:8-2；图：BER vs 抖动 |
| 8.8 | 工程实现要点与门禁（抖动容限、环路带宽、OSR 折中） | 综合 | 表：设计参数与验收口径 |

实验设计：

- **exp:8-1**：五类 TED 的 S 曲线与增益 $K_p$ 随滚降/翻转密度的变化（MATLAB 参考值 + Python 复现，两者误差 <5% 才可入书）。
- **exp:8-2**：ITR 2012 与 OPSP-VA 在介质抖动/时钟抖动/频偏下的 BER 对比（PSP 移植，固定 seed，输出 CSV + manifest）。

---

## 八、红线与风险

1. **不得整段照搬译本**：译本 CC BY-NC-ND 4.0（非商业、禁止演绎），本书为商业出版物，须改写为教学叙述；引用原文仅限短句并注明「译自 Rice 2009」。
2. **图全部重绘**：原书图版权归作者/出版商；用 `code/experiments/` 重新生成，manifest 登记来源。
3. **公式必须复核**：译本公式逐字节保留但空格拆散；引用前按第三节重排并与原书页核对。
4. **MATLAB 仓库无许可声明**：不直接分发其代码，只作算法参考与数值对拍；如需入仓，改写为 Python 并在附录 C 注明「参考 Igor Freire 实现」。
5. **PSP 的 `.venv` 不可用**：跑测试用系统 `python3 -m pytest tests -q`；`.venv/bin/python` 缺 pytest，会误报失败。
6. **PSP 数据与 seed**：BER CSV 绑定 `seed42`、`pw2.5`、`pmr` 条件；引用时必须同时声明抖动/频偏/OSR，否则不可比。
