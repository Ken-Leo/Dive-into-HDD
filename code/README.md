# 《深入浅出HDD》实验与代码库

本目录收录书中各章的可复现实验与仿真代码。目标是：**书中每一幅仿真图都能由这里的脚本一键重生成**，读者克隆仓库即可复现。

## 环境

- Python 3.11+（开发环境实测 3.13）
- 依赖见 `requirements.txt`：`pip install -r code/requirements.txt`
- 不需要联网；数据随仓库提供或由脚本生成。

## 快速开始

```bash
python code/experiments/ch05_pulse_shape.py --out figures/ch05/fig05-05-pulse-shape.png
python -m pytest code/tests -q
```

## 目录

| 路径 | 内容 |
|------|------|
| `hddbook/` | 共享库：信号生成、信道模型、检测/均衡工具、度量与绘图 |
| `experiments/` | 各章实验脚本，命名 `chNN_<slug>.py` |
| `tests/` | 冒烟与回归测试（小参数、短时长） |
| `data/` | 小型样例数据（≤10 MB/文件），每个数据集附 README |
| `requirements.txt` | 固定依赖 |

## 实验脚本规范（强制）

1. 每个脚本必须提供 `--seed`、`--out`、`--quick`（小参数快速跑）参数；`main()` 可被测试导入。
2. 输出：图（PNG+PDF）与结果 CSV（参数、指标、版本、时间戳），路径由 `--out` 决定。
3. 随机性统一走 `hddbook.config.rng(seed)`；禁止脚本内直接 `np.random.*` 无种子调用。
4. 数据加载走 `hddbook.io.load_dataset(name)`；禁止硬编码 `/Volumes/...` 或 `~/...` 绝对路径。
5. 脚本只做编排；算法进 `hddbook/`，避免复制粘贴。
6. 每个脚本配 `tests/test_<name>.py` 冒烟测试；运行超过 60 s 的标记 `@pytest.mark.slow`。
7. 图件必须在 `figures/manifest.yaml` 登记（图号、脚本、命令、数据、SHA256、版权）。

## 代码来源与许可

- 共享库与实验脚本为本项目原创（作者：罗可及贡献者），许可随仓库 LICENSE。
- 从既有研究项目（RSI4HDD、PRML-Explore、RLL、PSP、ABCForDisc 等）移植的算法，必须在文件头注明来源项目、原作者与移植日期；仅移植算法，不复制其数据。
- 外部数据（公司实测 HDD 信号）脱敏后入库；原始数据留在外部路径，由 `HDD_DATA_ROOT` 环境变量指定。

## 与书稿的对应

实验编号与章节对应关系见 `docs/plan/experiments.md`；图-代码映射见 `figures/manifest.yaml`。正文引用格式：`{{code:ch05_pulse_shape}}`、`{{exp:5-2}}`、`{{fig:5-5}}`。
