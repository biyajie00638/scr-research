---
layout: home

hero:
  name: "SCR脱硝系统CFD研究"
  text: "固定式工业SCR系统流场分析与优化"
  tagline: 喉道临界流 · 气液两相雾化 · 尿素喷射冷区管理 · Cu-SCR催化剂
  image:
    src: /images/scr-system.svg
    alt: SCR系统示意图
  actions:
    - theme: brand
      text: 查看项目
      link: /projects/scr-nz001
    - theme: alt
      text: 核心研究
      link: /research/critical-flow

features:
  - icon: 🔬
    title: 喉道临界流
    details: 基于CFD方法的喉道临界流参数验证与边界条件确定，为SCR系统流量精度提供理论依据。
    link: /research/critical-flow

  - icon: 💧
    title: 气液两相雾化
    details: 尿素溶液喷射后的液滴蒸发与热解过程模拟，分析雾化特性对流场和温度场的影响。
    link: /research/atomization

  - icon: 🌡️
    title: 冷区温度分析
    details: 尿素热解吸热与水分蒸发潜热导致催化剂局部温降的定量分析，优化喷射位置与控制策略。
    link: /research/urea-injection

  - icon: 📊
    title: 氨逃逸控制
    details: SCR系统中氨逃逸值与出口NOx测试值正比关系的机制分析与排放控制方案。
    link: /research/nh3-nox

  - icon: ⚙️
    title: 气助式喷射系统
    details: 气助式尿素喷射系统在长管路工况下的喷射量误差分析与优化建议。
    link: /system/air-assist

  - icon: 🧪
    title: Cu-SCR催化剂
    details: 铜基SCR催化剂性能参数、工作窗口与温度管理策略分析。
    link: /system/catalyst
---

## 项目简介

**SCR_NZ001** 是一个固定式工业SCR（选择性催化还原）脱硝系统项目，当前处于 CFD 流量验证阶段。本项目聚焦于以下核心技术问题：

<div class="research-card">

### 🎯 核心目标

1. **CFD流量验证** — 通过计算流体力学方法验证SCR系统内部流场均匀性与分布特性
2. **喉道临界流参数** — 确定喉道截面关键流动参数的边界条件与精确设置
3. **尿素喷射优化** — 分析尿素喷射位置、喷射量、雾化特性对脱硝效率的影响
4. **温度场管理** — 定量分析冷区温度下降幅度，优化催化剂温度分布均匀性

</div>

<div class="research-card">

### 📐 关键参数

| 参数类别 | 参数名称 | 研究状态 |
|---------|---------|---------|
| 喉道参数 | 临界流速、马赫数、压力比 | <span class="tag tag-blue">进行中</span> |
| 雾化参数 | SMD、喷雾锥角、液滴速度 | <span class="tag tag-orange">准备中</span> |
| 喷射参数 | 喷射量、喷射位置、管路压降 | <span class="tag tag-blue">进行中</span> |
| 催化剂参数 | 空速、温度窗口、活性 | <span class="tag tag-green">已完成</span> |

</div>

<div class="research-card">

### ⚡ 研究亮点

- **尿素热解吸热机制** — 深入分析尿素热解过程对催化剂局部温度的定量影响
- **气液两相耦合模拟** — 建立尿素溶液雾化-蒸发-热解全过程的CFD模型
- **氨逃逸相关性** — 确认氨逃逸值与出口NOx测试值的正比关系
- **长管路误差** — 量化气助式尿素喷射系统在实际长管路中的喷射量偏差

</div>

---

::: tip 技术栈
- **CFD软件**: 商用CFD求解器 + 自定义UDF
- **网格划分**: 结构化/非结构化混合网格
- **多相流模型**: VOF / Eulerian / DPM
- **化学反应**: SCR脱硝反应动力学模型
:::
