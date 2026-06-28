# NN-RFC-0003

# 语义融合协议

Version 1

## 摘要

语义融合协议定义了 nyanya LLM Agent 如何将部分 OSU 解释聚合、协调和合成为协调共识状态。本协议规定了融合流程、张力保留规则、ACI 对抗性审查流水线、CHC 与 ESL 失效模式检测，以及 DSR 延迟残留处理。本协议是 NN-RFC-0001 §5 中融合规则的执行层。

## 状态

协议规范。

参考文献：[NN-TR-2026-001](https://github.com/nya-lab/NN-TR-2026-001)，[NN-RFC-0001](https://github.com/nya-lab/NN-RFC-0001)。

## 1. 术语

`Merge`（融合）

将张力消解为协调状态的行为。Merge 是 nyanya LLM 流水线的第四阶段（Split → Flow → Field → Merge → Speak）。一次有效的融合应当保留未消解的张力，声明有损压缩，并允许结果状态被挑战。

`Consensus Cluster`（共识簇）

共享来源链且已收敛至兼容解释的一组 OSU 信号。共识簇不是最终答案——它是可被未来信号挑战的候选状态。

`Tension Preservation`（张力保留）

未消解的分歧必须在融合输出中继续传递的规则。张力不被消除，而是编码在输出 OSU 的 rho 字段中。

`CHC`（碳基级联认知偏差）

Cascade High-Confidence Cognitive Bias。一种失效模式：多个 OPU 基于共享的缺陷先验达到统一的高置信共识。CHC 比单单元偏差更危险，因为群体置信度掩盖了底层逻辑缺陷。

`ESL`（回声语义闭环）

Echo Semantic Loop。一种失效模式：OPU 之间反复循环相似表述，产生不断扩展的文本但新增有效信息趋近于零。ESL 由认知多样性密度 D 严重过低引发。

`DSR`（延迟语义残留）

Deferred Semantic Residue。无法即时整合到共识中的碎片语义。DSR 存储在 NLB 缓冲池中，等待延迟批量回收。

## 2. 协议目标

本协议优化以下目标：

- 从异构输入中计算加权共识；
- 可追溯的分歧保留；
- CHC 与 ESL 失效模式检测；
- 可逆融合决策；
- 高张力场景下的优雅降级。

## 3. 非目标

本协议不判定任何信号的真值。

本协议不保证所有张力都将被消解。

本协议不定义 Speak 阶段输出格式。

本协议不管理 OPU 生命周期或路由——这些由 Flow 和 OCML 处理。

## 4. 融合流水线

### 4.1 流水线阶段

```
Merge Pipeline:
  Collect → Group → Weight → Fuse → Inspect → Output
```

1. **Collect**：从 Field 收集当前任务窗口的所有 OSU 信号。
2. **Group**：按来源链对信号分区。
3. **Weight**：在每条链内计算加权共识。
4. **Fuse**：从链级结果组合统一输出 OSU。
5. **Inspect**：对融合输出执行 ACI 对抗性审查。
6. **Output**：将融合后的 OSU 写入 Field，若审查未通过则延迟至 NLB。

### 4.2 Collect 阶段

```
collect(field, task_window) -> OSU[]:
  return field.read({
    time_window: task_window,
    ttl > 0,
    category != NOISE
  })
```

NOISE 类别信号被排除在融合输入之外，以防止稀释共识质量。

### 4.3 Group 阶段

```
group(signals) -> Map<provenance_chain, OSU[]>:
  chains = {}
  for signal in signals:
    chain_id = hash(signal.provenance)
    chains[chain_id].append(signal)
  return chains
```

无来源的信号（Split 阶段的根信号）形成各自的单例链。

## 5. 加权共识

### 5.1 链级融合

对每条来源链，融合流程计算加权共识：

```
merge_chain(signals: OSU[]) -> ChainResult:
  consensus = Σ(omega_i * c_i) / Σ(omega_i)
  residual_tension = max(rho_i) 跨输入
  chain_confidence = harmonic_mean(omega_i)
  information_gain = max(0, eta_current - eta_previous)

  if residual_tension > T_threshold:
    return ChainResult {
      consensus: consensus,
      confidence: chain_confidence * (1 - residual_tension),
      tension: residual_tension,
      status: PENDING_INSPECTION
    }
  else:
    return ChainResult {
      consensus: consensus,
      confidence: chain_confidence,
      tension: residual_tension,
      status: ACCEPTED
    }
```

### 5.2 跨链合成

```
fuse(chain_results: ChainResult[]) -> OSU:
  1. 跨链聚合共识：
       final_c = weighted_average(chain_results, weight=confidence)
  2. final_omega = mean(chain_results.confidence)
  3. final_rho = max(chain_results.tension)
  4. final_eta = information_gain(
       final_c,
       previous_consensus_state
     )
  5. provenance = collect all input signal ids
  6. return OSU {
       c: final_c,
       omega: final_omega,
       tau: merge_computation_time,
       rho: final_rho,
       eta: final_eta,
       provenance: provenance,
       ttl: default_ttl
     }
```

### 5.3 有损压缩声明

若融合从输入信号中移除或抽象了任何信息，输出 OSU 必须在其 `c` 字段中包含压缩标注：

```
compression: {
  original_signal_count: N,
  merged_signal_count: 1,
  compression_ratio: 1/N,
  dropped_categories: [被丢弃的语义类别列表]
}
```

此声明确保下游消费者能够评估融合带来的信息损失。

## 6. ACI 对抗性审查

### 6.1 审查流水线

```
inspect(merged_osu: OSU, input_signals: OSU[]) -> InspectionResult:
  contradiction_score = measure_contradiction(merged_osu, input_signals)
  blindspot_score = detect_blindspots(merged_osu, input_signals)
  fragility_score = test_fragility(merged_osu, input_signals)

  A = max(contradiction_score, blindspot_score, fragility_score)

  if A > A_safety_threshold:
    return InspectionResult {
      passed: false,
      score: A,
      failure_reason: argmax(contradiction, blindspot, fragility)
    }
  else:
    return InspectionResult {
      passed: true,
      score: A
    }
```

### 6.2 审查维度

**矛盾度**：衡量融合共识是否被任何输入信号所反驳。高矛盾度得分表明融合压制了有效的异议。

```
Contradiction(z) = max( semantic_distance(z.c, signal_i.c) * signal_i.omega )
```

**盲区度**：检测融合共识是否遗漏了输入信号中存在但未出现在输出中的信息。

```
Blindspot(z) = 1 - (|information_retained| / |information_available|)
```

**脆弱度**：测试融合共识在移除单个高权重输入信号后是否崩溃。高脆弱度表明过度依赖狭窄的证据基础。

```
Fragility(z) = 1 - (consensus_quality_without_top_signal / consensus_quality_with_all_signals)
```

### 6.3 审查结果

- **通过（A <= threshold）**：融合输出被接受。写入 Field。
- **未通过（A > threshold）**：融合输出标记为 PENDING。路由至 NLB 缓冲池。请求更多差异化 OPU 信号。新信号到达后尝试二次收敛。

## 7. 失效模式检测

### 7.1 CHC 检测

CHC 在以下条件满足时被检测到：

```
CHC_condition = (
  cluster_confidence > C_high
  AND prior_diversity < D_low
  AND contradiction_score < epsilon
)
```

具有极高置信度、低先验多样性和近乎零内部矛盾的集群为 CHC 候选。检测触发：
- 立即执行 ACI 深度审查；
- 强制多样性注入：向低先验、高 D 的 OPU 请求信号；
- 降低当前共识的置信度。

### 7.2 ESL 检测

ESL 通过监测连续融合轮次的信息增益率来检测：

```
ESL_condition = (
  consecutive_rounds_with_eta_below_threshold > R_esl
  AND cluster_cognitive_diversity D < D_esl
)
```

当 ESL 被检测到时：
- MCP 提升 EPG 探索权重；
- Flow 增加多样性注入比例；
- LAXI 回收冗余语义残留。

## 8. DSR 延迟语义残留

### 8.1 残留分类

无法即时整合的碎片语义归类为 DSR：

```
classify_residue(unmerged_fragments: OSU[]) -> DSR[]:
  for fragment in unmerged_fragments:
    if fragment.eta < eta_min:
      标记为 LOW_VALUE —— 立即丢弃
    else if fragment.rho > rho_high:
      标记为 HIGH_TENSION —— 保留供未来挑战
    else:
      标记为 INCOMPLETE —— 保留等待补充信号
```

### 8.2 批量回收

```
reclaim_dsr(dsr_pool: DSR[], current_consensus: OSU) -> void:
  for dsr in dsr_pool:
    age = now - dsr.arrival_time
    if age > max_retention:
      丢弃 dsr
    else if dsr 匹配 current_consensus 领域:
      将 dsr 重新注入融合流水线
    else:
      保留 dsr 至下一周期
```

NLB 缓冲池定期执行批量回收，丢弃过期 DSR 并将相关片段重新注入融合流水线。

## 9. 融合可逆性

每次融合操作都是可逆的。输出 OSU 的 provenance 字段包含完整的输入信号 id 集合。下游消费者可以：

1. 从 Field 读取融合后的 OSU。
2. 追溯其 provenance 获取所有输入信号。
3. 使用不同参数或不同 OPU 集合重新执行融合。
4. 通过向 Field 写入 critique 信号来挑战融合结果。

此可逆性是协议"可被挑战的状态"保证的基础。

## 10. 实现说明

### 10.1 默认参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| T_threshold | 0.3 | 触发 ACI 审查的张力阈值 |
| A_safety_threshold | 0.5 | ACI 综合得分安全阈值 |
| C_high | 0.85 | CHC 检测的置信度阈值 |
| D_low | 0.2 | CHC 检测的多样性阈值 |
| R_esl | 3 | ESL 检测的连续低 eta 轮次 |
| D_esl | 0.3 | ESL 检测的多样性阈值 |
| eta_min | 0.05 | DSR 保留的最低 eta |
| rho_high | 0.7 | HIGH_TENSION DSR 的张力阈值 |
| max_retention | 600 s | DSR 最大保留时间 |
| default_ttl | 10 | 融合输出 OSU 的默认 TTL |

### 10.2 最小可行实现

符合规范的实现必须支持：

- Collect、Group、Weight、Fuse 流水线阶段（§4）；
- 带张力保留的链级加权共识（§5.1）；
- 带压缩声明的跨链合成（§5.2–§5.3）；
- 矛盾度、盲区度、脆弱度评分（§6.2）；
- ESL 检测（§7.2）。

以下为可选：

- ACI 对抗性审查流水线（§6.1）；
- CHC 检测（§7.1）；
- DSR 分类与批量回收（§8）；
- 融合可逆性支持（§9）。

## 11. 参考文献

- [NN-TR-2026-001] nyanya LLM: A Carbon-Based Neural-Fabric Foundation Model for Distributed Cognitive Coordination and Organic Cognitive Metabolism. nya-lab, 2026.
- [NN-RFC-0001] 语义共识协议 v1. nya-lab, 2026.
- [NN-RFC-0002] 动态路由与 Field 状态协议 v1. nya-lab, 2026.