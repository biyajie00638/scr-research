# SCR 设计智能助理

用于固定式发动机排气系统的 SCR 初步计算、设计复核和售前方案整理。这个公开实现基于已有技能的计算与工作流程整理，使用独立计算脚本和合成项目样例。

| 功能 | 输出 |
| --- | --- |
| 烟气条件与排放 | 标况与工况流量、干湿基、折氧、NOx 质量流量与排放因子 |
| 尿素投加 | 按入口 ANR 或目标去除量供氨倍率计算 DEF 理论需求 |
| 混合管与催化剂 | 截面、流速、有效混合长度、停留时间、有效体积与空速 |
| 售前方案 | 设备与电控接口核对、BOM 与预算口径、图纸及方案字段一致性 |

## 安装

**Codex**。复制完整的 [`scr-design-assistant`](scr-design-assistant/) 目录到项目的 `.agents/skills/` 或用户目录下的 `.agents/skills/`，在会话中使用 `$scr-design-assistant`。也可以用 `$skill-installer` 安装指向该技能子目录的 GitHub 链接。详见 [技能说明](https://learn.chatgpt.com/docs/build-skills)。

**ChatGPT**。下载 [技能 ZIP](scr-design-assistant.zip)，进入「插件 → 技能 → 创建 → 从电脑上传」，按页面提示完成。技能上传功能取决于账号和工作区设置。详见 [ChatGPT 技能帮助](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)。

## 本地试跑

计算脚本仅使用 Python 标准库。在仓库目录运行：

```sh
python scr-design-assistant/scripts/scr_calc.py scr-design-assistant/examples/engine.json
python -m unittest discover -s tests -v
```

合成样例的两种输入均得到入口 NOx 质量流量 0.495 kg/h（以 NO₂ 计）。GHSV 按装填且通气的 240 L 计算为 15,000 h⁻¹，高于样例采用的 14,000 h⁻¹约束。批量 JSON 中各计算独立执行，需要衔接的输入由调用方从前一步结果传入。

售前输出及边界见 [设计参考](scr-design-assistant/references/presales.md)。实际工程所需的性能和压降数据、设备库、图纸母版及项目报价由使用者提供。

## 许可证

公开文件采用 [MIT](LICENSE) 许可证。项目资料、性能报告及设备报价由各自权利人保留。
