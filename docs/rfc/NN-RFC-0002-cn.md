# NN-RFC-0002

# 动态路由与 Field 状态协议

Version 1

## 摘要

动态路由与 Field 状态协议定义了 nyanya LLM Agent 如何发现、分类和路由 OSU 信号通过 OPU 集群，以及如何从共享语义 Field 中读取和写入。本协议规定了信号分类体系、OPU 选择算法、负载均衡与多样性注入机制，以及 Field 状态原语。本协议是 NN-RFC-0001 §6 中路由规则的执行层。

## 状态

协议规范。

参考文献：[NN-TR-2026-001](https://github.com/nya-lab/NN-TR-2026-001)，[NN-RFC-0001](https://github.com/nya-lab/NN-RFC-0001)。

## 1. 术语

`Field`（场）

共享语义环境。所有 Agent 向 Field 贡献并从中读取。Field 是通过持续信号交换维护的分布式状态。它不是数据库——它是活的语义基板。

`Flow`（流）

将 OSU 信号路由通过 OPU 集群的行为。Flow 是 nyanya LLM 流水线的第二阶段（Split → Flow → Field → Merge → Speak）。Flow 决定*哪个* OPU 在*何时*处理*什么*信号。

`Route`（路由）

通过 OPU 集群的有向路径。路由是动态的，按信号计算，可因应张力、漂移或饱和而重新配置。

`Hotspot`（热点）

接收到不成比例路由流量的 OPU 或集群区域。热点降低吞吐量并增加语义漂移。

`Semantic Category`（语义类别）

由分类器分配给每条 OSU 信号的标签。类别决定路由优先级和 OPU 亲和度。

`Diversity Injection`（多样性注入）

将路由容量有意识地分配给低先验、高认知多样性 OPU 的行为。此举防止集群坍缩至单一推理路径。

## 2. 协议目标

本协议优化以下目标：

- 将信号递送至能力最强的 OPU 子集；
- 跨集群负载分配；
- 认知多样性保持；
- 热点避免；
- 低路由延迟。

## 3. 非目标

本协议不定义信号内容。

本协议不评估信号质量。

本协议不执行融合或共识操作。

本协议不替代 OCML 代谢层——它是在 OCML 调控下运行的路由基板。

## 4. Field 状态

### 4.1 Field 定义

Field 是一个分布式、仅追加的语义状态。它是 nyanya LLM 集群的共享记忆。

```
Field {
  entries:    OSU[]       // 有序信号日志
  tension_map: Map<id, rho>  // 每条信号链的当前张力
  drift_index: scalar      // 聚合语义漂移
  version:    uint         // 单调递增状态版本
}
```

### 4.2 Field 原语

```
write(field, osu):
  将 osu 追加至 entries
  更新 osu.provenance 链的 tension_map
  重新计算 drift_index
  递增 version

read(field, query) -> OSU[]:
  返回匹配查询过滤器的 entries
  查询可包含：来源链、语义类别、时间窗口、ttl > 0

subscribe(field, filter) -> stream<OSU>:
  返回匹配过滤器的 OSU entries 实时流
  供 Merge 阶段等待待处理信号使用
```

### 4.3 Field 垃圾回收

ttl = 0 的 entries 标记为过期。过期 entries 按可配置间隔压缩。压缩通过保留过期 entries 的 id 映射来保持来源链完整性。

## 5. 信号分类

### 5.1 分类体系

每条 OSU 信号在路由前被归类为以下语义类别之一：

| 类别 | 描述 | 路由优先级 |
|---|---|---|
| FACT | 事实断言，知识检索 | 高 |
| REASON | 逻辑推导，多步推理 | 中 |
| CREATIVE | 发散思维，新颖假设 | 低 |
| CRITIQUE | 反例，挑战信号 | 高 |
| WARNING | 风险标志，安全警报 | 关键 |
| FRAGMENT | 不完整推导，部分结果 | 低 |
| NOISE | 低信息量，高熵信号 | 降级 |

### 5.2 分类流程

```
classify(osu) -> Category:
  1. 从 osu.c 提取语义特征
  2. 计算类别亲和度得分
  3. 若 osu.rho > 0.6：
       提升为 CRITIQUE（高冲突信号需要优先路由）
  4. 若 osu.eta < 0.1：
       降级为 NOISE（低信息信号浪费路由容量）
  5. 返回 argmax(亲和度得分)
```

## 6. 动态路由

### 6.1 OPU 选择

```
route(signal, cluster) -> OPU[]:
  1. category = classify(signal)
  2. candidate_set = cluster.filter(opu =>
       opu.s_i 匹配信号领域
       AND opu.r_i >= task_complexity(signal)
       AND opu.a_i > A_min
     )
  3. 若 candidate_set 为空：
       放宽约束：降低 r_i 阈值，扩展领域匹配
  4. 按适配度得分排序 candidate_set：
       fitness = w1 * domain_match + w2 * capacity_headroom + w3 * (1 - load)
  5. 选择 top-k OPU（k = target_parallelism）
  6. 应用多样性注入（§6.2）
  7. 返回选中 OPU
```

### 6.2 多样性注入

路由器为低先验、高 D 的 OPU 保留可配置比例的容量：

```
diversity_injection(candidates, fraction=0.2):
  diverse_set = candidates.filter(opu =>
    opu.s_i 先验匹配度低 BUT opu.D 高于阈值
  )
  inject_count = ceil(total_capacity * fraction)
  将 inject_count 个多样性 OPU 加入最终路由集合
  从最终集合中移除 inject_count 个最低适配度候选
```

此举确保固定比例的路由容量始终分配给认知多样性 OPU，防止集群收敛至单一推理路径。

### 6.3 负载均衡

```
balance(cluster, routes):
  for each opu in cluster:
    if opu.load > L_high:
      标记 opu 为饱和
      将溢出信号重定向至次优候选
    if opu.load < L_low:
      标记 opu 为未充分利用
      增加该 opu 的多样性注入权重
```

### 6.4 路由稳定性

路由按信号计算。协议不在信号之间缓存路由。但对于同一来源链内的信号，路由器施加粘性偏差：处理过上游信号的 OPU 在候选集中获得更高权重，减少上下文切换开销。

## 7. RES Guard 集成

Flow 模块与 RES Guard（NN-RFC-0001 §6.2）集成，检测并响应递归调度退化：

```
RES = R_repeat / (R_novel + epsilon)

if RES > threshold_1:
  轮换活跃 OPU 集合，增加多样性注入比例
if RES > threshold_2:
  重构 Split 阶段任务分解
if RES > threshold_3:
  停止路由，输出当前共识并附不确定性标注
```

Flow 模块在每次路由决策后向 RES Guard 报告 R_repeat 和 R_novel 指标。

## 8. Field 一致性

### 8.1 张力传播

当 OPU 向 Field 写入高 rho 信号时，协议向所有订阅受影响来源链的 OPU 广播张力通知。此举触发对先前共识的重新评估，并可能启动新一轮信号生成。

### 8.2 漂移监测

Field 漂移指数计算为：

```
drift_index = mean( semantic_distance(osu_i.c, re_encode(osu_i)) )
```

跨所有活跃 OSU entries。当 drift_index 超过全局阈值时，协议触发 Field 压缩事件，丢弃低置信 entries 并将 Field 状态重新锚定到高置信共识簇。

## 9. 实现说明

### 9.1 默认参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| A_min | 0.2 | 路由资格的最低可用注意力 |
| target_parallelism | 3 | 每条信号路由的默认 OPU 数量 |
| diversity_fraction | 0.2 | 为多样性 OPU 保留的路由容量 |
| L_high | 0.8 | 饱和负载阈值 |
| L_low | 0.3 | 未充分利用负载阈值 |
| drift_threshold | 0.15 | Field 漂移指数压缩触发值 |
| compaction_interval | 1000 signals | Field 压缩频率 |

### 9.2 最小可行实现

符合规范的实现必须支持：

- Field 写入、读取和订阅原语（§4）；
- 七类别分类体系的信号分类（§5）；
- 带适配度评分的动态 OPU 选择（§6.1）；
- 多样性注入（§6.2）；
- RES Guard 指标上报（§7）。

以下为可选：

- Field 漂移监测与压缩（§8.2）；
- 来源链粘性路由偏差（§6.4）。

## 10. 参考文献

- [NN-TR-2026-001] nyanya LLM: A Carbon-Based Neural-Fabric Foundation Model for Distributed Cognitive Coordination and Organic Cognitive Metabolism. nya-lab, 2026.
- [NN-RFC-0001] 语义共识协议 v1. nya-lab, 2026.