---
name: scr-design-assistant
description: Use for preliminary SCR engineering and presales design for stationary engines and exhaust systems. Check emission bases, calculate reagent demand and duct geometry, screen catalyst space velocity, and prepare traceable equipment, electrical BOM, budget, and proposal drafts.
---

# SCR 设计智能助理

用用户提供的发动机工况、排放资料和项目边界，完成 SCR 初步设计或审核。默认用用户当前的技术术语和输出语言。先判断所需模块，再选用计算路径，按需要读后面的专业参考。

## 计算

1. 记录工况、单位、温压基准、干湿基、参考氧、污染物质量当量与出处。并列展示冲突的候选值。关键参数缺失时，输出可算部分并列明待补条件。
2. 使用 `scripts/scr_calc.py` 对标况与工况流量、干湿基、NOx 质量排放、DEF 投加、管路和催化剂做可重复计算。运行 `python scripts/scr_calc.py --help` 查看入口。以排放浓度或已知排放因子作为对应路线的输入。仅在两套输入独立且工况、口径一致时作交叉校验。
3. 记录入口 ANR 或去除量供氨倍率的采用值和定义。实际干基浓度与对应干标况流量配对。分别报告理论 DEF、设计泵流量和候选泵工作点。
4. 计算混合管净截面积、流速、有效长度和停留时间，根据现场可用长度判断布置。采用经核实的阻力系数、厂家曲线或实测依据另核压降。
5. 按实际参与反应的装填体积计算 GHSV，并独立记录采购及备用量。结合对应厂家性能资料检查工况温度、空速和系统背压。缺资料时标明估算或待核的指标。

## 售前交付

需要设备选型、电控、预算或技术方案时，阅读 [售前设计参考](references/presales.md)。先固定当前项目采用值，再按规则匹配可用设备库。用同一份计算与配置快照填写售前 P&ID、接口简图、设备表、BOM、预算和方案。只有获得可用母版时才生成对应图纸；缺价时展示已计价小计和待询项。保留技术审查需要的来源与修订信息。

设备库与项目资料由使用者提供。将附带的样例只用于复算或练习。工程适用性、排放承诺和整柜认证状态按对应项目证据填写。
