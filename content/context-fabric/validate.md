# validate

Module: `cfabric_benchmarks.corpora.validate`
Source: https://context-fabric.ai/docs/api/cfabric_benchmarks/corpora/validate

Validate Text-Fabric corpora loading in both Text-Fabric and Context-Fabric.

Tests each corpus with:
1. Text-Fabric loading from `.tf` files
2. Context-Fabric loading from `.tf` files (which auto-compiles to `.cfm`)
3. Context-Fabric loading from `.cfm` cache

Also samples feature values from both `.tf` and `.cfm` loading paths to verify
data integrity through the compile/load cycle.

Tests each corpus one at a time to ensure clean memory state and accurate error
attribution.

## Usage

```bash
python benchmarks/validate_corpora.py
python benchmarks/validate_corpora.py --corpus bhsa   # Test single corpus
```

## Entry point

`main()`

## Classes

### CorpusStats
Statistics from loading a corpus.

**Attributes**

| Name | Type | Description |
| --- | --- | --- |
| `edge_features` | `int` | — |
| `error` | `str \| None` | — |
| `max_node` | `int` | — |
| `max_slot` | `int` | — |
| `node_features` | `int` | — |
| `node_types` | `int` | — |
| `samples` | `FeatureSamples \| None` | — |

**Constructor**

```python
__init__(
    self,
    max_slot: int = 0,
    max_node: int = 0,
    node_types: int = 0,
    node_features: int = 0,
    edge_features: int = 0,
    samples: FeatureSamples | None = None,
    error: str | None = None,
) -> None
```

---

### FeatureSamples
Sampled feature values for validation.

**Attributes**

| Name | Type | Description |
| --- | --- | --- |
| `edge_samples` | `dict[str, list[tuple[int, int, Any]]]` | — |
| `node_samples` | `dict[str, list[tuple[int, Any]]]` | — |
| `text_samples` | `list[tuple[int, str]]` | — |

**Constructor**

```python
__init__(
    self,
    node_samples: dict[str, list[tuple[int, Any]]],
    edge_samples: dict[str, list[tuple[int, int, Any]]],
    text_samples: list[tuple[int, str]],
) -> None
```

---

### ValidationResult
Result of validating a single corpus.

**Attributes**

| Name | Type | Description |
| --- | --- | --- |
| `cf_mmap_ok` | `bool` | — |
| `cf_mmap_stats` | `CorpusStats` | — |
| `cf_ok` | `bool` | — |
| `cf_stats` | `CorpusStats` | — |
| `corpus` | `str` | — |
| `mmap_stats_match` | `bool` | Check that `.cfm` loading produces same stats as `.tf` loading. |
| `samples_match` | `bool` | Check that feature value samples match between `.tf` and `.cfm` loading. |
| `stats_match` | `bool` | — |
| `tf_ok` | `bool` | — |
| `tf_stats` | `CorpusStats` | — |

**Constructor**

```python
__init__(
    self,
    corpus: str,
    tf_stats: CorpusStats,
    cf_stats: CorpusStats,
    cf_mmap_stats: CorpusStats,
) -> None
```

**Methods**

- `get_sample_mismatches(self) -> list[str]` — Get list of features with mismatched samples.

## Functions

- `clear_caches(tf_path: Path) -> None`
  Clear Text-Fabric and Context-Fabric cache directories.

- `load_with_context_fabric(tf_path: Path, collect_samples: bool = False) -> CorpusStats`
  Load corpus with Context-Fabric and return stats.

- `load_with_text_fabric(tf_path: Path) -> CorpusStats`
  Load corpus with Text-Fabric and return stats.

- `print_summary(results: list[ValidationResult]) -> None`
  Print summary table of all results.

- `sample_feature_values(api, sample_size: int = 100) -> FeatureSamples`
  Sample feature values from loaded API for validation. Samples nodes at regular
  intervals across the corpus to get representative coverage.

- `validate_corpus(corpus_name: str, corpus_dir: Path) -> ValidationResult`
  Validate a single corpus with both TF and CF.
