# NN-RFC-0002

# Dynamic Routing and Field State Protocol

Version 1

## Abstract

The Dynamic Routing and Field State Protocol defines how nyanya LLM agents discover, classify, and route OSU signals through the OPU cluster, and how they read from and write to the shared semantic Field. It specifies the signal classification taxonomy, the OPU selection algorithm, the load-balancing and diversity injection mechanisms, and the Field state primitives. This protocol is the execution layer for the routing rules defined in NN-RFC-0001 §6.

## Status

Protocol specification.

References: [NN-TR-2026-001](https://github.com/nya-lab/NN-TR-2026-001), [NN-RFC-0001](https://github.com/nya-lab/NN-RFC-0001).

## 1. Terms

`Field`

The shared semantic environment. All agents contribute to and read from the Field. The Field is a distributed state maintained through continuous signal exchange. It is not a database — it is a living semantic substrate.

`Flow`

The act of routing OSU signals through the OPU cluster. Flow is the second stage of the nyanya LLM pipeline (Split → Flow → Field → Merge → Speak). Flow determines *which* OPU processes *what* signal, *when*.

`Route`

A directed path through the OPU cluster. Routes are dynamic, computed per-signal, and may be reconfigured in response to tension, drift, or saturation.

`Hotspot`

An OPU or cluster region that receives a disproportionate share of routing traffic. Hotspots degrade throughput and increase semantic drift.

`Semantic Category`

A label assigned to each OSU signal by the classifier. Categories determine routing priority and OPU affinity.

`Diversity Injection`

The deliberate allocation of routing capacity to low-prior, high-cognitive-diversity OPUs. This prevents the cluster from collapsing into a narrow reasoning path.

## 2. Protocol Goals

The protocol optimizes for:

- signal delivery to the most capable OPU subset;
- load distribution across the cluster;
- cognitive diversity preservation;
- hotspot avoidance;
- low routing latency.

## 3. Non-Goals

The protocol does not define the content of signals.

The protocol does not evaluate signal quality.

The protocol does not perform merge or consensus operations.

The protocol does not replace the OCML metabolic layer — it is a routing substrate that operates under OCML regulation.

## 4. Field State

### 4.1 Field Definition

The Field is a distributed, append-only semantic state. It is the shared memory of the nyanya LLM cluster.

```
Field {
  entries:    OSU[]       // ordered signal log
  tension_map: Map<id, rho>  // current tension per signal chain
  drift_index: scalar      // aggregate semantic drift
  version:    uint         // monotonic state version
}
```

### 4.2 Field Primitives

```
write(field, osu):
  append osu to entries
  update tension_map for osu.provenance chain
  recompute drift_index
  increment version

read(field, query) -> OSU[]:
  return entries matching query filter
  query may include: provenance chain, semantic category, time window, ttl > 0

subscribe(field, filter) -> stream<OSU>:
  return live stream of OSU entries matching filter
  used by Merge stage to await pending signals
```

### 4.3 Field Garbage Collection

Entries with ttl = 0 are marked as expired. Expired entries are compacted on a configurable interval. The compaction preserves provenance chains by retaining the id mappings of expired entries.

## 5. Signal Classification

### 5.1 Taxonomy

Every OSU signal is classified into one of the following semantic categories before routing:

| Category | Description | Routing Priority |
|---|---|---|
| FACT | Factual assertions, knowledge retrieval | High |
| REASON | Logical derivation, multi-step inference | Medium |
| CREATIVE | Divergent thinking, novel hypotheses | Low |
| CRITIQUE | Counterexamples, challenge signals | High |
| WARNING | Risk flags, safety alerts | Critical |
| FRAGMENT | Incomplete derivations, partial results | Low |
| NOISE | Low-information, high-entropy signals | Deprioritized |

### 5.2 Classification Procedure

```
classify(osu) -> Category:
  1. extract semantic features from osu.c
  2. compute category affinity scores
  3. if osu.rho > 0.6:
       promote to CRITIQUE (high-conflict signals need priority routing)
  4. if osu.eta < 0.1:
       demote to NOISE (low-information signals waste routing capacity)
  5. return argmax(affinity scores)
```

## 6. Dynamic Routing

### 6.1 OPU Selection

```
route(signal, cluster) -> OPU[]:
  1. category = classify(signal)
  2. candidate_set = cluster.filter(opu =>
       opu.s_i matches signal domain
       AND opu.r_i >= task_complexity(signal)
       AND opu.a_i > A_min
     )
  3. if candidate_set is empty:
       relax constraints: lower r_i threshold, expand domain match
  4. sort candidate_set by fitness score:
       fitness = w1 * domain_match + w2 * capacity_headroom + w3 * (1 - load)
  5. select top-k OPUs (k = target_parallelism)
  6. apply diversity injection (§6.2)
  7. return selected OPUs
```

### 6.2 Diversity Injection

The router reserves a configurable fraction of capacity for low-prior, high-D OPUs:

```
diversity_injection(candidates, fraction=0.2):
  diverse_set = candidates.filter(opu =>
    opu.s_i has low prior match BUT opu.D is above threshold
  )
  inject_count = ceil(total_capacity * fraction)
  add inject_count diverse OPUs to final routing set
  remove inject_count lowest-fitness candidates from final set
```

This ensures that a fixed percentage of routing capacity is always allocated to cognitively diverse OPUs, preventing the cluster from converging on a single narrow reasoning path.

### 6.3 Load Balancing

```
balance(cluster, routes):
  for each opu in cluster:
    if opu.load > L_high:
      mark opu as saturated
      redirect overflow signals to next-best candidates
    if opu.load < L_low:
      mark opu as underutilized
      increase diversity injection weight for this opu
```

### 6.4 Route Stability

Routes are computed per-signal. The protocol does not cache routes between signals. However, for signals within the same provenance chain, the router applies a sticky bias: OPUs that processed upstream signals are weighted higher in the candidate set, reducing context-switching overhead.

## 7. RES Guard Integration

The Flow module integrates with RES Guard (NN-RFC-0001 §6.2) to detect and respond to recursive scheduling degradation:

```
RES = R_repeat / (R_novel + epsilon)

if RES > threshold_1:
  rotate active OPU set, increase diversity injection fraction
if RES > threshold_2:
  restructure Split-stage task decomposition
if RES > threshold_3:
  halt routing, output current consensus with uncertainty annotation
```

The Flow module reports R_repeat and R_novel metrics to RES Guard after each routing decision.

## 8. Field Consistency

### 8.1 Tension Propagation

When an OPU writes a high-rho signal to the Field, the protocol broadcasts a tension notification to all OPUs subscribed to the affected provenance chain. This triggers re-evaluation of prior consensus and may initiate a new round of signal generation.

### 8.2 Drift Monitoring

The Field drift index is computed as:

```
drift_index = mean( semantic_distance(osu_i.c, re_encode(osu_i)) )
```

across all active OSU entries. When drift_index exceeds the global threshold, the protocol triggers a Field compaction event, discarding low-confidence entries and re-anchoring the Field state to high-confidence consensus clusters.

## 9. Implementation Notes

### 9.1 Default Parameters

| Parameter | Default | Description |
|---|---|---|
| A_min | 0.2 | Minimum available attention for routing eligibility |
| target_parallelism | 3 | Default number of OPUs per signal route |
| diversity_fraction | 0.2 | Routing capacity reserved for diverse OPUs |
| L_high | 0.8 | Load threshold for saturation |
| L_low | 0.3 | Load threshold for underutilization |
| drift_threshold | 0.15 | Field drift index trigger for compaction |
| compaction_interval | 1000 signals | Field compaction frequency |

### 9.2 Minimum Viable Implementation

A conforming implementation must support:

- Field write, read, and subscribe primitives (§4);
- Signal classification into the seven-category taxonomy (§5);
- Dynamic OPU selection with fitness scoring (§6.1);
- Diversity injection (§6.2);
- RES Guard metric reporting (§7).

The following are optional:

- Field drift monitoring and compaction (§8.2);
- Sticky routing bias for provenance chains (§6.4).

## 10. References

- [NN-TR-2026-001] nyanya LLM: A Carbon-Based Neural-Fabric Foundation Model for Distributed Cognitive Coordination and Organic Cognitive Metabolism. nya-lab, 2026.
- [NN-RFC-0001] Semantic Consensus Protocol v1. nya-lab, 2026.