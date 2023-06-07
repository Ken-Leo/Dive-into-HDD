# 深入浅出HDD

本项目用于起草创作中国国内第一部尽可能深入介绍机械硬盘 HDD 技术的专业技术书籍。本书作者：罗可以及其他社区贡献者，
GitHub地址：https://github.com/Ken-Leo/Dive-into-HDD

## 项目背景

当今人类社会是一个由数字驱动的世界，全球数据总量持续增长，而其增速也越来越快。根据独立研究机构国际数据公司(International Data Corporation, IDC)开展的一项全球技术调研《数据新视界(Rethink Data)》，报告显示从 2015 年至 2025 年，每年新产生的数据量按照 26\% 的年复合增长率不断增加，今天每小时产生的数据量比 20 年前每年产生的数据量还多。预计到 2025 年全世界数字信息总量将达到 175.8 ZB(Zettabytes，泽字节)，为 2015 年的近十倍，其中近 80\% 的数据将被存储在传统数据中心、云数据中心和企业强化的边缘基础设施中。数据挖掘、人工智能、边缘计算和物联网等技术的广泛应用使得大量数据迁移至企业级数据仓库中。急剧增长的数据存储需求推动了磁存储、半导体存储和光存储等各类存储技术的进步。数据的存储方式和存储位置极大地影响了数据的经济价值，而大容量存储则是规模经济的推动力，因而以希捷科技公司(Seagate Technology LLC)为代表的数据存储企业重点关注存储面密度的发展，密度的增长使得存储设备可以在单位空间存储更多数据。综合考虑大容量、高带宽和安全性等因素，企业分布数据的存储介质遵循“90/10”规则，即 90\% 的数据存储在磁存储机械硬盘(Hard Disk Drive，HDD)中，而 10\% 的数据存储在半导体设备如固态硬盘(Solid State Drive，SSD)中。

与 SSD 相比，HDD 具有不可替代的优势。HDD 是磁存储设备发展的主力军，目前与半导体存储设备 SSD 的竞争较大，两者的基本功能及使用方法相同，且在产品外形和尺寸上也基本一致；尽管目前 SSD 具有处理速度快的优势，HDD 仍然具有多方面的优势：价格低、容量大、数据易恢复、写入次数无限制等，未来难以被完全替代。两类存储介质对当今世界的信息存储都至关重要，二者缺一不可，国内 SSD 已有相关产业如长江存储， SSD 的发展势头良好。然而，如今国内 HDD 技术的发展同电子芯片产业一样，受到国外的垄断和[限制](https://www.commerce.senate.gov/2021/10/committee-investigation-suggests-leading-technology-company-violated-huawei-related-rule)。为应对全世界数据存储的迫切需求和数据资产安全等外部不确定性因素，开展高密度大容量 HDD 磁记录技术的研究，对于各国做好自主可控的存储技术储备与建立相关产业尤为重要。

## 简介

本书尽可能覆盖 HDD 技术的各个层面，从学术研究的角度出发，主要介绍磁存储技术在学术研究及工业理论验证阶段的主要内容。本仓库主要包含 docs 和 figures 两个文件夹，其中 docs 文件夹用于存放本书《深入浅出HDD》各章节 markdown 格式的内容，而 figures 文件夹用于存放对应各章节所需的图片，未来计划争取以正式形式面向全社会读者出版，内容上可能会和正式书籍存在差别。如果您是相关领域的学者或对本书涉及的技术感兴趣，欢迎对本项目做出贡献或提出 issue。

## 面向人群

本项目面向对大容量数据存储设备技术包括但不限于 HDD、SSD、磁带及光盘感兴趣的朋友，特别是数据存储技术专业的研究生及数据存储产业的相关人士。本项目所涉及的技术知识可能需要您具有一定的数学如线性代数、积分、概率论、信息论和通信原理的知识基础，当然作者会尽可能以通俗简洁的叙述向大家展开介绍。由于作者本人的知识局限，难免存在错误和不当之处，烦请各位专家指正。

## 本书目录

 * [1.简介](docs/introduction.md#introduction)
 * [2.数据存储技术简介](docs/intro_data_storage.md#intro_data_storage)
   * [机械硬盘](docs/hdd.md#hdd)
   * [固态硬盘](docs/ssd.md#ssd)
   * [磁带](docs/tape.md#tape)
   * [光盘](docs/od.md#od)
   * [机械硬盘发展史](docs/history.md#history)
 * [3.磁记录技术研究现状](docs/research_status.md#research_status)
   * [一维磁记录](docs/one_diemnsional.md#one_diemnsional)
   * [二维磁记录](docs/two_dimensional.md#two_dimensional)
   * [三维磁记录](docs/three_dimensional.md#three_dimensional)
 * [4.通道模型](docs/channel.md#channel)
   * [写通道模型](docs/write_channel.md#write_channel)
   * [介质模型](docs/media_model.md#media_model)
   * [读通道模型](docs/read_channel.md#read_channel)
   * [噪声](docs/noise.md#noise)
 * [5.均衡技术](docs/equalization.md#equalization)
   * [线性均衡](docs/linear_equation.md#linear_equation)
   * [非线性均衡](docs/nonlinear_equation.md#nonlinear_equation)
 * [6.检测技术](docs/detection.md#detection)
   * [极大似然序列检测](docs/mlsd.md#mlsd)
   * [最大后验概率检测](docs/map.md#map)
   * [机器学习检测](docs/ml.md#ml)
 * [7.差错控制编解码](docs/ecc.md#ecc)
 * [8.约束编解码](docs/rll.md#rll)
 * [9.磁记录数据存取通道技术](docs/scheme.md#scheme)
 * [10.其他存储技术](docs/else.md#else)
   * [磁带技术及其发展](docs/tape_tech.md)
   * [光盘技术及其发展](docs/od_tech.md)
 * [Todo]

持续更新中……

## 引用


如果您在研究中使用了本项目请引用：

```bibraries
@book{luoke2023,
    title={深入浅出HDD},
    author={罗可 and 陈进才 and 卢萍},
    note={\url{https://github.com/Ken-Leo/Dive-into-HDD}},
    year={2023}
}
```

