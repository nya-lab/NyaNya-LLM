# NN-RFC-0003

# Semantic Merge Protocol

Version 1

## Abstract

The Semantic Merge Protocol defines how nyanya LLM agents aggregate, reconcile, and synthesize partial OSU interpretations into a coordinated consensus state. It specifies the merge procedure, the tension preservation rules, the ACI adversarial inspection pipeline, the CHC and ESL failure mode detection, and the DSR deferred residue handling. This protocol is the execution layer for the merge rules defined in NN-RFC-0001 §5.

## Status

Protocol specification.

References: [NN-TR-2026-001](https://github.com/nya-lab/NN-TR-2026-001), [NN-RFC-0001](https://github.com/nya-lab/NN-RFC-0001).

## 1. Terms

`Merge`

The act of resolving tension into a coordinated state. Merge is the fourth stage of the nyanya LLM pipeline (Split → Flow → Field → Merge → Speak). A valid merge preserves unresolved tension, declares lossy compression, and leaves the resulting state challengeable.

`Consensus Cluster`

A group of OSU signals that share a provenance chain and have converged on a compatible interpretation. A consensus cluster is not a final answer — it is a candidate state that may be challenged by future signals.

`Tension Preservation`

The rule that unresolved disagreement must be carried forward in the merged output. Tension is not eliminated; it is encoded in the output OSU's rho field.

`CHC`

Cascade High-Confidence Cognitive Bias. A failure mode where multiple OPUs reach a unified high-confidence consensus based on a shared flawed prior. CHC is more dangerous than single-unit bias because the group's confidence masks the underlying logical defect.

`ESL`

Echo Semantic Loop. A failure mode where OPUs repeatedly recycle similar formulations, producing expanding text with near-zero information gain. ESL is caused by critically low cognitive diversity density D.

`DSR`

Deferred Semantic Residue. Fragmented semantics that cannot be immediately integrated into the consensus. DSR is stored in the NLB buffer pool for delayed batch reclamation.

## 2. Protocol Goals

The protocol optimizes for:

- weighted consensus from heterogeneous inputs;
- traceable disagreement preservation;
- CHC and ESL failure mode detection;
- reversible merge decisions;
- graceful degradation under high-tension scenarios.

## 3. Non-Goals

The protocol does not determine the truth value of any signal.

The protocol does not guarantee that all tension will be resolved.

The protocol does not define the Speak stage output format.

The protocol does not manage OPU lifecycles or routing — those are handled by Flow and OCML.

## 4. Merge Pipeline

### 4.1 Pipeline Stages

```
Merge Pipeline:
  Collect → Group → Weight → Fuse → Inspect → Output
```

1. **Collect**: Gather all OSU signals from the Field for the current task window.
2. **Group**: Partition signals by provenance chain.
3. **Weight**: Compute weighted consensus within each chain.
4. **Fuse**: Compose a unified output OSU from chain-level results.
5. **Inspect**: Run ACI adversarial inspection on the fused output.
6. **Output**: Write the merged OSU to the Field, or defer to NLB if inspection fails.

### 4.2 Collect Stage

```
collect(field, task_window) -> OSU[]:
  return field.read({
    time_window: task_window,
    ttl > 0,
    category != NOISE
  })
```

NOISE-category signals are excluded from merge input to prevent dilution of consensus quality.

### 4.3 Group Stage

```
group(signals) -> Map<provenance_chain, OSU[]>:
  chains = {}
  for signal in signals:
    chain_id = hash(signal.provenance)
    chains[chain_id].append(signal)
  return chains
```

Signals with no provenance (root signals from the Split stage) form their own singleton chains.

## 5. Weighted Consensus

### 5.1 Chain-Level Merge

For each provenance chain, the merge procedure computes a weighted consensus:

```
merge_chain(signals: OSU[]) -> ChainResult:
  consensus = Σ(omega_i * c_i) / Σ(omega_i)
  residual_tension = max(rho_i) across inputs
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

### 5.2 Cross-Chain Fusion

```
fuse(chain_results: ChainResult[]) -> OSU:
  1. aggregate consensus across chains:
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

### 5.3 Lossy Compression Declaration

If the merge removes or abstracts any information from the input signals, the output OSU must include a compression annotation in its `c` field:

```
compression: {
  original_signal_count: N,
  merged_signal_count: 1,
  compression_ratio: 1/N,
  dropped_categories: [list of discarded semantic categories]
}
```

This declaration ensures that downstream consumers can assess the information loss incurred by the merge.

## 6. ACI Adversarial Inspection

### 6.1 Inspection Pipeline

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

### 6.2 Inspection Dimensions

**Contradiction**: Measures whether the merged consensus is contradicted by any input signal. High contradiction scores indicate that the merge suppressed valid dissent.

```
Contradiction(z) = max( semantic_distance(z.c, signal_i.c) * signal_i.omega )
```

**Blindspot**: Detects whether the merged consensus omits information present in input signals but absent from the output.

```
Blindspot(z) = 1 - (|information_retained| / |information_available|)
```

**Fragility**: Tests whether the merged consensus collapses when a single high-weight input signal is removed. High fragility indicates over-reliance on a narrow evidence base.

```
Fragility(z) = 1 - (consensus_quality_without_top_signal / consensus_quality_with_all_signals)
```

### 6.3 Inspection Outcomes

- **Passed (A <= threshold)**: Merge output is accepted. Written to Field.
- **Failed (A > threshold)**: Merge output is marked PENDING. Routed to NLB buffer pool. Additional differentiated OPU signals are requested. Secondary convergence is attempted after new signals arrive.

## 7. Failure Mode Detection

### 7.1 CHC Detection

CHC is detected when:

```
CHC_condition = (
  cluster_confidence > C_high
  AND prior_diversity < D_low
  AND contradiction_score < epsilon
)
```

A cluster with extremely high confidence, low prior diversity, and near-zero internal contradiction is a CHC candidate. The detection triggers:
- Immediate ACI deep inspection;
- Forced diversity injection: request signals from low-prior, high-D OPUs;
- Confidence downgrade on the current consensus.

### 7.2 ESL Detection

ESL is detected by monitoring the information gain rate across consecutive merge rounds:

```
ESL_condition = (
  consecutive_rounds_with_eta_below_threshold > R_esl
  AND cluster_cognitive_diversity D < D_esl
)
```

When ESL is detected:
- MCP increases EPG exploration weight;
- Flow increases diversity injection fraction;
- LAXI recycles redundant semantic residue.

## 8. DSR Deferred Semantic Residue

### 8.1 Residue Classification

Fragmented semantics that cannot be immediately integrated are classified as DSR:

```
classify_residue(unmerged_fragments: OSU[]) -> DSR[]:
  for fragment in unmerged_fragments:
    if fragment.eta < eta_min:
      mark as LOW_VALUE — discard immediately
    else if fragment.rho > rho_high:
      mark as HIGH_TENSION — retain for future challenge
    else:
      mark as INCOMPLETE — retain for supplementary signals
```

### 8.2 Batch Reclamation

```
reclaim_dsr(dsr_pool: DSR[], current_consensus: OSU) -> void:
  for dsr in dsr_pool:
    age = now - dsr.arrival_time
    if age > max_retention:
      discard dsr
    else if dsr matches current_consensus domain:
      re-inject dsr into merge pipeline
    else:
      retain dsr for next cycle
```

The NLB buffer pool periodically executes batch reclamation, discarding expired DSR and re-injecting relevant fragments into the merge pipeline.

## 9. Merge Reversibility

Every merge operation is reversible. The output OSU's provenance field contains the complete set of input signal ids. A downstream consumer can:

1. Read the merged OSU from the Field.
2. Trace its provenance to retrieve all input signals.
3. Re-execute the merge with different parameters or a different OPU set.
4. Challenge the merge by writing a critique signal to the Field.

This reversibility is the foundation of the protocol's "challengeable state" guarantee.

## 10. Implementation Notes

### 10.1 Default Parameters

| Parameter | Default | Description |
|---|---|---|
| T_threshold | 0.3 | Tension threshold for ACI inspection trigger |
| A_safety_threshold | 0.5 | ACI composite score safety threshold |
| C_high | 0.85 | Confidence threshold for CHC detection |
| D_low | 0.2 | Diversity threshold for CHC detection |
| R_esl | 3 | Consecutive low-eta rounds for ESL detection |
| D_esl | 0.3 | Diversity threshold for ESL detection |
| eta_min | 0.05 | Minimum eta for DSR retention |
| rho_high | 0.7 | Tension threshold for HIGH_TENSION DSR |
| max_retention | 600 s | Maximum DSR retention time |
| default_ttl | 10 | Default TTL for merged OSU output |

### 10.2 Minimum Viable Implementation

A conforming implementation must support:

- Collect, Group, Weight, and Fuse pipeline stages (§4);
- Chain-level weighted consensus with tension preservation (§5.1);
- Cross-chain fusion with compression declaration (§5.2–§5.3);
- Contradiction, blindspot, and fragility scoring (§6.2);
- ESL detection (§7.2).

The following are optional:

- ACI adversarial inspection pipeline (§6.1);
- CHC detection (§7.1);
- DSR classification and batch reclamation (§8);
- Merge reversibility support (§9).

## 11. References

- [NN-TR-2026-001] nyanya LLM: A Carbon-Based Neural-Fabric Foundation Model for Distributed Cognitive Coordination and Organic Cognitive Metabolism. nya-lab, 2026.
- [NN-RFC-0001] Semantic Consensus Protocol v1. nya-lab, 2026.
- [NN-RFC-0002] Dynamic Routing and Field State Protocol v1. nya-lab, 2026.