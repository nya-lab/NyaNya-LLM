# NN-RFC-0001

# Semantic Consensus Protocol

Version 1

## Abstract

The Semantic Consensus Protocol defines how nyanya LLM agents exchange, compare, and merge partial interpretations without reducing them to token-level agreement. It specifies the message format, routing, merge rules, anomaly handling, and steady-state constraints for the nyanya LLM distributed reasoning pipeline.

## Status

Protocol specification. Supersedes Draft 0.

References: [NN-TR-2026-001](https://github.com/nya-lab/NN-TR-2026-001).

## 1. Terms

`Field`

The shared semantic environment. All agents contribute to and read from the Field. The Field is not a database — it is a distributed state maintained through continuous signal exchange.

`Signal`

A bounded interpretation emitted by an agent. Signals are the only unit of communication in the protocol. Every signal carries provenance, confidence, and tension.

`Tension`

A conflict between compatible but incomplete interpretations. Tension is not an error — it is the raw material for consensus. The protocol preserves tension rather than resolving it prematurely.

`Merge`

The act of resolving tension into a coordinated state. A valid merge preserves unresolved tension, declares lossy compression, and leaves the resulting state challengeable.

`Drift`

Loss of meaning caused by repeated summarization or unstable routing. Drift is measured as the semantic distance between a signal and its re-encoded form after passing through the protocol stack.

`OSU`

Organic Semantic Unit. The minimum standardized carrier for cross-node transmission. Defined in §2.

`OPU`

Organic Processing Unit. A heterogeneous cognitive agent in the CBNF fabric. Defined in NN-TR-2026-001 §5.1.

`Route`

A directed path through the OPU cluster. Routes are dynamic and may be reconfigured in response to tension, drift, or saturation.

## 2. Protocol Goals

The protocol optimizes for:

- coherence across agents;
- traceable disagreement;
- low semantic drift;
- reversible merges;
- concise state transfer.

## 3. Non-Goals

The protocol does not define truth.

The protocol does not claim biological plausibility.

The protocol does not replace model inference.

The protocol does not prescribe a specific consensus algorithm. It defines the message format and rules; the underlying consensus mechanism is implementation-defined.

## 4. OSU Message Format

Every signal in the protocol is encoded as an OSU (Organic Semantic Unit). The OSU is the minimum standardized carrier for OPU external output and cross-node transmission.

### 4.1 Encoding Structure

```
osu {
  id:        string       // unique signal identifier
  source:    agent_id     // originating OPU
  c:         semantic     // core semantic content (§4.2)
  omega:     scalar       // local confidence weight [0, 1]
  tau:       ms           // generation latency
  rho:       scalar       // viewpoint conflict coefficient [0, 1]
  eta:       scalar       // information increment coefficient [0, 1]
  provenance: ref[]       // upstream OSU references
  ttl:       uint         // remaining hop count
}
```

### 4.2 Core Semantic Content

The `c` field carries the payload. It may contain:

- local conclusions;
- counterexamples;
- reasoning experience;
- visual associations;
- logical疑点;
- risk warnings;
- incomplete derivation fragments.

The `c` field is opaque to the routing layer. Its internal structure is defined by the consuming OPU.

### 4.3 Field Semantics

- `omega` — confidence. Higher values indicate stronger local conviction. The protocol uses omega for weighted voting, but does not treat high omega as truth.
- `tau` — latency. The wall-clock time the OPU spent generating this signal. Used by NLB to classify slow-reasoning fragments.
- `rho` — conflict. Indicates how strongly this signal disagrees with the current consensus. High rho signals are prioritized for ACI inspection.
- `eta` — novelty. Measures how much new information this signal contributes relative to existing signals. Low eta triggers BES saturation detection.
- `provenance` — traceability. Every signal must reference its upstream OSUs. This enables reversible merges and drift measurement.
- `ttl` — hop limit. Decremented at each routing hop. Signals with ttl=0 are discarded. Prevents infinite routing loops.

## 5. Merge Rules

### 5.1 Validity Conditions

A merge is valid when:

- input signals preserve provenance;
- unresolved tension is carried forward;
- lossy compression is declared;
- the resulting state can be challenged by a later signal.

### 5.2 Merge Procedure

```
merge(signals: OSU[]) -> OSU:
  1. group signals by provenance chain
  2. for each chain:
     a. compute weighted consensus: Σ(omega_i * c_i) / Σ(omega_i)
     b. residual tension = max(rho_i) across inputs
     c. if residual tension > T_threshold:
          mark output as "pending-inspection"
          enqueue for ACI verification
  3. compose output OSU:
     c = aggregated consensus
     omega = harmonic mean of input omegas
     rho = residual tension
     eta = information gain relative to previous consensus
     provenance = input signal ids
```

### 5.3 ACI Inspection

The Adversarial Consensus Inspection (ACI) mechanism performs multi-layer reverse verification on high-confidence consensus clusters. When a merged output exceeds the safety threshold:

```
A = max(Contradiction(z), Blindspot(z), Fragility(z))
```

where z is the consensus cluster under inspection. If A exceeds the safety threshold, the conclusion is marked as pending and routed to the NLB asynchronous buffer pool, awaiting supplementary signals from differentiated OPUs before secondary convergence.

## 6. Routing Protocol

### 6.1 Dynamic Routing

The Flow module routes signals through the OPU cluster according to:

```
route(signal, cluster) -> OPU[]:
  1. classify signal by semantic category
  2. select OPUs where:
     - s_i (semantic prior) matches signal domain
     - r_i (reasoning capacity) meets task complexity
     - a_i (available attention) exceeds minimum threshold
  3. apply load-balancing: distribute signals to avoid hotspot saturation
  4. inject diversity: reserve 20% of capacity for low-prior, high-D OPUs
```

### 6.2 RES Guard

The Recursive Scheduling Degradation (RES) Guard monitors routing repetition:

```
RES = R_repeat / (R_novel + epsilon)
```

Tiered intervention:

- **Mild (RES > threshold_1)**: rotate active OPU set, introduce idle units with high cognitive diversity D.
- **Moderate (RES > threshold_2)**: restructure the Split-stage task decomposition, break existing fixed routing paths.
- **Severe (RES > threshold_3)**: force-terminate the cyclic scheduling link, output current consensus with uncertainty annotation, halt non-incremental compute consumption.

## 7. Anomaly Handling

### 7.1 LAXI Monitoring

The Large-Scale Adaptive Experience Interaction (LAXI) interface continuously monitors five anomaly categories:

- cognitive fatigue accumulation;
- semantic feature drift;
- repeated scheduling redundancy;
- high-entropy semantic accumulation;
- consensus convergence阻塞.

Composite anomaly indicator:

```
Lambda_i = gamma_1 * F_i + gamma_2 * S_i + gamma_3 * A_i + gamma_4 * R_i
```

where:
- F_i: unit fatigue degree;
- S_i: semantic drift magnitude;
- A_i: anomaly output proportion;
- R_i: cyclic scheduling frequency.

### 7.2 Tiered Disposal

When Lambda_i exceeds the threshold, the node enters metabolic disposal status:

1. unit weight衰减;
2. local context clearing;
3. anomaly signal标记滞留;
4. routing link switching;
5. unit temporary休眠;
6. fallback to low-risk reasoning path.

Fragmented semantics that cannot be immediately integrated are classified as DSR (Deferred Semantic Residue) and processed in delayed batch回收.

## 8. Steady-State Constraints

### 8.1 CCL Equalization

The Cognitive Potential Equalization Circuit (CCL) monitors unit heat:

```
T_i = w_e * E_i + w_v * V_i + w_h * H_i
```

When T_i exceeds the global safety threshold, the circuit自动下调s the unit's global voting weight, blocking global viewpoint偏移 caused by unrestrained unilateral cognitive potential expansion.

### 8.2 Coordination Scaling Law

Cluster performance P is bounded by:

```
P = A * N^alpha * K^beta * (1 - sigma)^gamma * D^mu
```

The protocol must operate within the optimal interval:
- sigma (conflict density): moderate, avoiding both collapse (sigma -> 0) and saturation (sigma过高);
- D (cognitive diversity density): sufficient to prevent ESL echo semantic loops;
- N (active OPU count): increased only when accompanied by proportional D growth.

### 8.3 BES Saturation

The protocol monitors Base Execution Saturation:

```
BES = Repeat(OSU) / (Novel(OSU) + epsilon)
```

When BES exceeds the threshold, the MCP protocol下调s the corresponding unit task quota, and LAXI synchronously回收s redundant semantic residue.

## 9. Implementation Notes

### 9.1 Default Parameters

| Parameter | Default | Description |
|---|---|---|
| T_threshold | 0.3 | Tension threshold for ACI inspection |
| RES threshold_1 | 0.4 | Mild degradation trigger |
| RES threshold_2 | 0.7 | Moderate degradation trigger |
| RES threshold_3 | 1.2 | Severe degradation trigger |
| w_e | 0.4 | CCL emotional activation weight |
| w_v | 0.3 | CCL confidence weight |
| w_h | 0.3 | CCL hostility weight |
| delta | 500 ms | NLB latency threshold |
| theta_1 | 0.3 | BEW complexity分流 threshold |

### 9.2 Minimum Viable Implementation

A conforming implementation must support:

- OSU message encoding and decoding (§4);
- Merge with tension preservation (§5);
- Dynamic routing with diversity injection (§6.1);
- RES Guard monitoring (§6.2);
- LAXI anomaly detection (§7.1).

The following are optional:

- ACI inspection (§5.3);
- CCL equalization (§8.1);
- BES saturation detection (§8.3).

## 10. References

- [NN-TR-2026-001] nyanya LLM: A Carbon-Based Neural-Fabric Foundation Model for Distributed Cognitive Coordination and Organic Cognitive Metabolism. nya-lab, 2026.