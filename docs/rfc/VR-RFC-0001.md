# VR-RFC-0001

# Semantic Consensus Protocol

Draft 0

## Abstract

The Semantic Consensus Protocol defines how Vallace agents exchange, compare,
and merge partial interpretations without reducing them to token-level
agreement.

## Status

Fictional protocol draft.

## 1. Terms

`Field`

The shared semantic environment.

`Signal`

A bounded interpretation emitted by an agent.

`Tension`

A conflict between compatible but incomplete interpretations.

`Merge`

The act of resolving tension into a coordinated state.

`Drift`

Loss of meaning caused by repeated summarization or unstable routing.

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

## 4. Message Shape

```text
signal {
  id: string
  source: agent
  claim: semantic_state
  confidence: scalar
  tension: tension_vector
  provenance: references
}
```

## 5. Merge Rules

A merge is valid when:

- input signals preserve provenance;
- unresolved tension is carried forward;
- lossy compression is declared;
- the resulting state can be challenged by a later signal.

## 6. Open Questions

- How should tension be represented?
- When should unresolved disagreement remain visible?
- What is the minimum viable provenance format?
