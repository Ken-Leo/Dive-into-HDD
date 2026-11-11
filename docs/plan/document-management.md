# 《深入浅出HDD》文档与资产管理规范（V1.0 · 2026-11-11）

> 目的：让书稿、图件、实验代码、数据、素材台账与审校记录**同源、可追溯、可复现、可审校**，避免「正文引用找不到图/代码/数据」「同一图多处版本不一致」「素材版权说不清」。
> 关联：[实施计划](implementation-plan.md) · [知识资产总图](knowledge-assets.md) · [实验与代码体系](experiments.md) · [进度追踪](progress.md)

---

## 一、目录结构（唯一合法布局）

```
Dive-into-HDD/
├── docs/
│   ├── chapters/                 # 正文：chNN-<slug>.md
│   ├── plan/                     # 策划与台账（本目录）
│   ├── templates/                # 章节模板
│   └── archive/                  # 废弃稿/旧版本（保留原因与日期）
├── figures/
│   ├── chNN/                     # figNN-MM-<slug>.{drawio,svg,png}
│   ├── manifest.yaml             # 图-代码-数据映射台账（唯一真源）
│   └── license.csv               # 图版权台账
├── code/
│   ├── hddbook/                  # 共享库（信道/检测/绘图/度量）
│   ├── experiments/              # chNN_<slug>.py 可运行实验
│   ├── tests/                    # 冒烟与回归测试
│   ├── data/                     # 小型样例数据（≤10 MB/文件）
│   └── requirements.txt
├── tools/                        # 文档一致性检查脚本
└── README.md                     # 中英双语（英文在前）
```

**禁止**：正文直接引用仓库外绝对路径；图件散落在 `docs/`；代码依赖 `~/Downloads` 或 `/Volumes/Elements` 的绝对路径（外部素材必须先复制/转换进仓库或由环境变量指定）。

---

## 二、命名与编号

| 对象 | 规则 | 示例 |
|------|------|------|
| 章节正文 | `docs/chapters/chNN-<slug>.md` | `ch05-recording-channel.md` |
| 图件 | `figures/chNN/figNN-MM-<slug>.<ext>` | `figures/ch05/fig05-05-pulse-shape.png` |
| 图源文件 | 同名 `.drawio`/`.svg`/`.py` | `fig05-05-pulse-shape.py` |
| 实验脚本 | `code/experiments/chNN_<slug>.py` | `ch05_pulse_shape.py` |
| 数据 | `code/data/<slug>/` + `README.md` | `code/data/pmr-sample/` |
| 交叉引用 ID | `sec:5.2` `eq:5-4` `fig:5-3` `tab:5-2` `exp:5-2` `code:ch05_pulse_shape` | 正文用 `{{fig:5-3}}` 占位，导出时替换 |
| 提交 | 英文，`docs:`/`code:`/`figures:` 前缀 | `docs: complete chapter 5 draft` |
| 里程碑标签 | `v0.1-sample` `v0.5-draft` `v1.0-manuscript` | 仅打在全稿检查通过后 |

---

## 三、元数据（每章/每图/每脚本必须）

章节 frontmatter 至少包含：`title`、`chapter`、`status`、`version`、`target_pages`、`target_hanzi`、`source_assets`（素材台账 ID 列表）、`figures`（图号列表）、`experiments`（实验 ID 列表）、`reviewers`、`license`、`last_updated`。

图件台账 `figures/manifest.yaml` 每条：

```yaml
- figure_id: fig:5-5
  chapter: 5
  section: "5.3.2"
  title: "纵向孤立重放脉冲与 Voigt 拟合"
  script: code/experiments/ch05_pulse_shape.py
  command: "python code/experiments/ch05_pulse_shape.py --out figures/ch05/fig05-05-pulse-shape.png"
  data: code/data/pmr-sample/params.json
  output_sha256: "<生成后回填>"
  source: "原创重绘（参考编码书 Ch2 图2.5）"
  license: "CC BY 4.0（原创）"
  status: draft | verified
```

**规则**：正文出现的每个图号必须在 manifest 中存在；manifest 中的脚本必须能一键重生成该图；`output_sha256` 用于回归校验（允许因字体/后端差异而人工复核后更新）。

---

## 四、资产台账（`docs/plan/asset-registry.csv`）

字段：`asset_id,type,path,title,source,license,chapters,usage,status,risk,owner,last_checked`。
`type` 取值：`translation`（译稿）、`paper`（论文）、`knowledge_base`（OpenKB）、`experiment`（实验项目）、`data`（实测/仿真数据）、`report`（项目报告）、`figure`（图）、`code`（脚本）。
`usage` 取值：`theory`（理论素材）、`experiment`（实验）、`figure`（图源）、`data`（数据）、`citation`（文献）、`reference`（仅参考）。
**所有正文素材引用必须指向台账中的 `asset_id`**；新增素材先入台账再使用。

---

## 五、数据管理

1. **数据分级**：公开（论文/开源）→ 可入库；公司实测（HDD 原型信号）→ 脱敏后入库，原始数据留在外部路径并由环境变量 `HDD_DATA_ROOT` 指向。
2. **入库阈值**：单文件 ≤10 MB、单目录 ≤100 MB；超出用脚本生成或提供下载说明 + SHA256。
3. **格式**：CSV/JSON/NPZ（禁止 .mat 作为唯一格式，需转换脚本）；每个数据集附 `README.md`（来源、采集条件、参数、许可、校验和）。
4. **可复现**：所有实验必须固定随机种子；数据加载走 `hddbook.io.load_dataset(name)`，禁止脚本内硬编码绝对路径。

---

## 六、代码规范（与[实验与代码体系](experiments.md)一致）

- Python 3.11+，依赖固定于 `code/requirements.txt`；禁止联网下载（数据入库或提供缓存）。
- 每个实验脚本：`argparse` 参数、`--seed`、`--out`、日志、结果 CSV + 图；`main()` 可被测试调用。
- 共享逻辑进 `code/hddbook/`；脚本只做编排，不复制粘贴算法。
- 每个脚本配 `code/tests/test_<name>.py` 冒烟测试（小参数、短时长、断言输出存在与数值范围）。
- 运行时间 >60 s 的实验标记 `slow`，CI 只跑 smoke。

---

## 七、审校与质量记录

- `docs/plan/review-log.md`：每章记录审读人、轮次、问题清单、结论（通过/返工）、日期。
- 每章交付前必须通过[实施计划第 7 节质量门禁](implementation-plan.md) + 本规范第五/六节检查。
- 图件与代码的变更须同步更新 manifest 与章节引用；**禁止只改图不改正文**。
- 重大结论变更在 `docs/plan/decisions.md` 记录（决策、依据、影响章节、日期）。

---

## 八、自动化一致性检查（`tools/check_docs.py`，随写作逐步实现）

检查项：
1. 章节 frontmatter 完整、`status` 合法。
2. 正文引用的 `fig:`/`tab:`/`eq:`/`code:` ID 均存在。
3. `figures/manifest.yaml` 每条脚本存在、命令可解析、输出路径在 `figures/`。
4. 术语与 `docs/plan/terminology.md` 一致（黑名单：读通道/磁碟等）。
5. 参考文献条目可解析（DOI/ISBN 格式）且正文引用编号存在。
6. 字数与页数估算在预算 ±10%。
7. 无仓库外绝对路径（正则 `/Volumes/`、`~/`）。

CI/本地钩子：提交前跑 `python tools/check_docs.py --changed`；失败则阻止提交（可用 `--force` 记录原因）。

---

## 九、版本与归档

- 章节状态：`outline → drafting → author-review → figures → qa → done`；状态变更写入 `progress.md` 并提交。
- 废弃内容移入 `docs/archive/<date>-<slug>/`，保留 README 说明废弃原因与被替代版本。
- 里程碑打 tag；tag 前必须全稿检查通过。
- 每章完成后生成 `docs/chapters/chNN-*.md` 的 PDF/HTML 预览（可选，用于审读）。

---

## 十、职责与协作

| 角色 | 职责 |
|------|------|
| 作者 | 技术审校、工程经验补充、最终签字 |
| 写作助手 | 素材包、初稿、图件脚本、一致性检查 |
| 审读人（2 位） | 技术核验 + 体例语言审读，填 review-log |
| 资产管理员（可由助手兼） | 台账维护、版权与数据合规、manifest 校验 |

**协作纪律**：同一文件同一时间只由一人修改；跨文件改动先在任务板登记写范围；提交前跑检查脚本；每日同步进度表。
