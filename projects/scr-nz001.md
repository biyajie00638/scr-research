# SCR_NZ001 项目概述

<span class="tag tag-blue">进行中</span> <span class="tag tag-orange">CFD流量验证</span>

## 项目背景

**SCR_NZ001** 是针对固定式工业SCR（选择性催化还原）脱硝系统开展的CFD分析项目。项目目标是通过计算流体力学方法，精确验证SCR系统内部流场特性，为系统设计优化提供理论依据和数据支持。

## 系统构成

```mermaid
flowchart LR
    A[烟气入口] --> B[尿素喷射区]
    B --> C[混合段]
    C --> D[Cu-SCR催化剂层]
    D --> E[洁净烟气出口]
    G[空气压缩机] --> H[气助式喷嘴]
    F[尿素溶液罐] --> H
    H --> B
```

## 技术路线

### 1. CFD建模

| 项目 | 参数设置 |
|------|---------|
| 求解器类型 | 稳态/瞬态压力基求解器 |
| 湍流模型 | Realizable k-ε / SST k-ω |
| 多相流模型 | 欧拉-拉格朗日 (DPM) |
| 化学反应 | SCR脱硝反应动力学 |
| 网格类型 | 结构化/非结构化混合网格 |
| 网格数量 | ~500万 ~ 2000万 |

### 2. 边界条件

- **入口**: 速度入口 / 质量流量入口
- **出口**: 压力出口
- **壁面**: 无滑移壁面（标准壁面函数）
- **催化剂层**: 多孔介质模型 + 化学反应源项

### 3. 验证指标

1. 催化剂入口截面速度均匀性指数 (UI)
2. NH3/NOx 摩尔比分布均匀性
3. 催化剂层温度分布均匀性
4. 系统总压降
5. 尿素液滴蒸发完成率

## 当前阶段

当前处于 **CFD流量验证参数准备阶段**，重点推进：

- <span class="tag tag-blue">喉道临界流</span> 参数确定与边界条件设置
- <span class="tag tag-orange">气液两相雾化模拟</span> 关键参数标定
- <span class="tag tag-blue">尿素喷射位置</span> 优化与冷区评估

## 参考文献

1. SCR DeNOx system CFD modeling guidelines
2. ANSYS Fluent Theory Guide - Multiphase Flows
3. Cu-SCR catalyst reaction kinetics
