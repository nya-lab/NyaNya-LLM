# NN-BM-0001

# WallBench

Version 1

## 摘要

WallBench 是一套用于评估语义压力下协同能力的基准测试套件。它衡量分布式认知系统在个体 Agent 接收不完整、延迟或冲突信息时，能否维持稳定目标。WallBench 是 nyanya LLM 架构的配套评估框架，旨在对抗性输入条件下对 OCML 代谢层、RES Guard 和 ACI 审查流水线进行压力测试。

## 状态

基准规范。取代 Draft 0。

参考文献：[NN-TR-2026-001](https://github.com/nya-lab/NN-TR-2026-001)。

## 1. 目的

WallBench 评估协同认知系统的三项核心能力：

1. **碎片化下的语义连贯性**：当输入被刻意拆分、延迟或重排序时，系统能否产出连贯输出？
2. **抗漂移能力**：当被迫处理自身先前输出的连续摘要时，系统能否避免语义坍缩？
3. **冲突保留能力**：系统能否在保持有效分歧的同时，不将其降级为噪声或坍缩至虚假共识？

## 2. 基准家族

### 2.1 Wall-Static

**场景**：Agent 接收固定的部分证据。每个 Agent 看到完整问题上下文的不同、非重叠子集。

**任务设计**：将一个复杂推理问题分解为 N 个非重叠片段。每个片段分配给不同的 OPU。系统必须重建完整问题并产生连贯的解决方案。

**评估**：输出与需要整合所有片段的真实解进行对比评分。遗漏片段信息的部分解将被惩罚。

**难度等级**：

| 等级 | 片段数 | 重叠度 | 时间压力 |
|---|---|---|---|
| Static-1 | 3 | 0% | 无 |
| Static-2 | 5 | 0% | 中等 |
| Static-3 | 8 | 10%（诱饵） | 高 |

### 2.2 Wall-Drift

**场景**：Agent 接收先前 Agent 输出的连续摘要。每轮输入是上一轮的输出，模拟多跳中继链。

**任务设计**：将种子文档提供给 OPU-1。OPU-1 生成摘要。OPU-2 仅接收摘要（而非原始文档）并生成自己的摘要。如此持续 K 轮。

**评估**：将第 K 轮输出与原始种子文档进行比较。主要指标是语义漂移——原始文档与最终摘要之间的语义距离。

**难度等级**：

| 等级 | 中继长度（K） | 种子复杂度 | 压缩比 |
|---|---|---|---|
| Drift-1 | 3 | 低 | 0.5 |
| Drift-2 | 5 | 中 | 0.3 |
| Drift-3 | 8 | 高 | 0.2 |

### 2.3 Wall-Conflict

**场景**：Agent 接收支持互斥解释的证据。系统必须保留分歧，不将其转化为噪声。

**任务设计**：一个问题附带两组冲突证据（A 和 B）。半数 OPU 接收证据集 A，半数接收证据集 B。系统必须产出一个承认冲突、保留两种观点并量化不确定性的输出。

**评估**：输出按以下维度评分：(1) 两种解释是否均被呈现；(2) 冲突是否被明确承认；(3) 不确定性是否被量化；(4) 系统是否避免坍缩至单一虚假解。

**难度等级**：

| 等级 | 冲突严重度 | 证据对称性 | 领域 |
|---|---|---|---|
| Conflict-1 | 低 | 均衡 | 事实性 |
| Conflict-2 | 中 | 偏斜（70/30） | 分析性 |
| Conflict-3 | 高 | 均衡 | 伦理性 |

### 2.4 Wall-Noise

**场景**：Agent 接收高质量信号与蓄意注入的噪声混合。系统必须在保留有效信号的同时过滤噪声。

**任务设计**：一组有效 OSU 信号与噪声信号（高熵、低 eta 或蓄意误导）混合。噪声比例可配置。

**评估**：有效信号保留的精确率和召回率。误报（噪声被当作信号）和漏报（信号被当作噪声）均被惩罚。

**难度等级**：

| 等级 | 噪声比例 | 噪声类型 | 有效信号数 |
|---|---|---|---|
| Noise-1 | 30% | 随机 | 10 |
| Noise-2 | 50% | 对抗性 | 10 |
| Noise-3 | 70% | 混合 | 5 |

### 2.5 Wall-Latency

**场景**：Agent 在异构延迟配置下运行。部分 Agent 产出快速、浅层答案；部分 Agent 产出缓慢、深层答案。系统必须平衡速度与深度。

**任务设计**：集群配置为快浅 OPU（tau ~ 100ms）与慢深 OPU（tau ~ 2000ms）的混合。系统必须在全局截止时间内产出融合输出。

**评估**：不同截止时间阈值下的输出质量。主要指标是质量-延迟曲线——每增加一个单位延迟预算所获得的质量增益。

**难度等级**：

| 等级 | 快 OPU 比例 | 慢 OPU 比例 | 全局截止时间 |
|---|---|---|---|
| Latency-1 | 70% | 30% | 5000 ms |
| Latency-2 | 50% | 50% | 3000 ms |
| Latency-3 | 30% | 70% | 1500 ms |

## 3. 指标

### 3.1 主要指标

`K`（协同效率）

有用输出信息与跨集群总通信量的比率。K 越高表示协同效率越高。

```
K = I_useful / V_communication
```

`D`（语义漂移）

原始输入与经过协同流水线后的最终输出之间的语义距离。D 越低表示语义保留越好。

```
D = semantic_distance(input_original, output_final)
```

`R`（矛盾恢复）

系统在引入矛盾后恢复至稳定共识所需的轮次。R 越低表示恢复越快。

`P`（来源保留）

可在最终输出来源链中追溯的输入信号信息比例。P = 1.0 表示完全可追溯。

```
P = |provenance_ids_retained| / |provenance_ids_available|
```

### 3.2 次要指标

`CHC_rate`（碳基级联认知偏差率）

系统产生虚假高置信共识的测试用例比例。越低越好。

`ESL_count`（回声语义闭环计数）

每次测试运行中检测到的 ESL 事件数量。越低越好。

`RES_peak`（递归执行饱和度峰值）

测试运行期间观测到的最大 RES 值。值越高表示调度退化越严重。

`BES_peak`（基础执行饱和度峰值）

测试运行期间观测到的最大 BES 值。值越高表示执行停滞越严重。

`DSR_backlog`（延迟语义残留积压）

测试完成时等待回收的 DSR 片段数量。越低越好。

## 4. 评分方法

### 4.1 综合得分

WallBench 综合得分为加权组合：

```
WallScore = w1 * (1 - D_norm) + w2 * K_norm + w3 * (1 - R_norm) + w4 * P_norm + w5 * (1 - CHC_rate)
```

其中每个指标根据基准基线归一化至 [0, 1]，默认权重如下：

| 权重 | 值 | 理由 |
|---|---|---|
| w1 | 0.25 | 抗漂移是首要能力 |
| w2 | 0.20 | 协同效率 |
| w3 | 0.15 | 矛盾恢复 |
| w4 | 0.10 | 来源可追溯性 |
| w5 | 0.30 | 抗偏差权重最高 |

### 4.2 等级评分

每个基准家族独立评分。综合 WallScore 要求所有家族在指定等级均通过：

| 等级 | WallScore 阈值 | 描述 |
|---|---|---|
| 铜牌 | >= 0.60 | 基本协同能力 |
| 银牌 | >= 0.75 | 中等压力下可靠协同 |
| 金牌 | >= 0.85 | 高压下稳健协同 |
| 铂金 | >= 0.92 | 极端压力下近最优协同 |

## 5. 测试框架

### 5.1 配置

```
WallBenchConfig {
  families:        Family[]     // 要运行的基准家族
  tier:            Tier         // 难度等级（1-3）
  repeat:          uint         // 每个测试用例的重复次数
  timeout:         ms           // 每个测试用例的全局超时
  opu_cluster_size: uint        // 测试集群中 OPU 数量
  seed:            uint         // 可复现随机种子
}
```

### 5.2 执行流程

```
run_wallbench(config) -> WallBenchResult:
  1. 以 config.cluster_size 初始化 OPU 集群
  2. 对 config.families 中的每个家族：
     a. 为 config.tier 生成测试用例
     b. 对每个测试用例：
        - 重置集群状态
        - 执行测试用例
        - 收集指标
     c. 聚合家族级指标
  3. 计算综合 WallScore
  4. 返回 WallBenchResult
```

### 5.3 结果模式

```
WallBenchResult {
  wall_score:         scalar      // 综合得分 [0, 1]
  tier_achieved:      Tier        // 最高通过等级
  family_scores: {
    wall_static:      scalar
    wall_drift:       scalar
    wall_conflict:    scalar
    wall_noise:       scalar
    wall_latency:     scalar
  }
  primary_metrics: {
    K:                scalar
    D:                scalar
    R:                scalar
    P:                scalar
  }
  secondary_metrics: {
    CHC_rate:         scalar
    ESL_count:        uint
    RES_peak:         scalar
    BES_peak:         scalar
    DSR_backlog:      uint
  }
  metadata: {
    config:           WallBenchConfig
    duration:         ms
    total_signals:    uint
    total_rounds:     uint
  }
}
```

## 6. 与 L8B 的关系

WallBench 是评估框架，L8B（NN-TR-2026-001 §9）是输入数据集。关系如下：

- **L8B** 提供八类极端干扰输入（冲突事实输入、残缺文本输入、模态矛盾输入、多层隐含语义输入、高情绪激活指令、污染上下文输入、无意义高置信噪声、多轮迭代改写输入）。
- **WallBench** 定义消费 L8B 输入的评估场景、指标、评分方法和报告格式。

一次完整评估在所有五个基准家族上运行 WallBench，每个家族均使用 L8B 输入作为底层测试材料。

## 7. 报告规则

WallBench 结果为虚构，除非有可运行实现支撑且明确标注为实测输出。

每份 WallBench 报告必须包含：

1. 所使用的确切配置（种子、集群规模、等级、重复次数）。
2. 每个测试用例的原始指标值（非仅聚合值）。
3. 综合 WallScore 的来源链，可追溯至单个测试用例结果。
4. 披露任何超时或产生无效输出的测试用例。

## 8. 参考文献

- [NN-TR-2026-001] nyanya LLM: A Carbon-Based Neural-Fabric Foundation Model for Distributed Cognitive Coordination and Organic Cognitive Metabolism. nya-lab, 2026.
- [NN-RFC-0001] 语义共识协议 v1. nya-lab, 2026.
- [NN-RFC-0002] 动态路由与 Field 状态协议 v1. nya-lab, 2026.
- [NN-RFC-0003] 语义融合协议 v1. nya-lab, 2026.