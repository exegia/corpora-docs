# API Reference: cfabric

> Source: [https://context-fabric.ai/docs/api/cfabric](https://context-fabric.ai/docs/api/cfabric)

Context-Fabric: A graph-based corpus engine for annotated text.

This package provides tools for loading, navigating, and querying annotated text corpora using a graph-based data model.

## Basic Usage

```python
>>> import cfabric
>>> CF = cfabric.Fabric(locations='path/to/corpus')
>>> api = CF.load('feature1', 'feature2')
>>> for node in api.F.feature1.s('value'):
...     print(api.T.text(node))
```

## Submodules

| Module | Description |
|--------|-------------|
| [core](https://context-fabric.ai/docs/api/cfabric/core) | Core API of Context-Fabric |
| [describe](https://context-fabric.ai/docs/api/cfabric/describe) | Corpus description utilities |
| [downloader](https://context-fabric.ai/docs/api/cfabric/downloader) | Corpus downloader |
| [features](https://context-fabric.ai/docs/api/cfabric/features) | Feature data models |
| [io](https://context-fabric.ai/docs/api/cfabric/io) | Data loading and compilation |
| [navigation](https://context-fabric.ai/docs/api/cfabric/navigation) | Corpus navigation |
| [precompute](https://context-fabric.ai/docs/api/cfabric/precompute) | Pre-computation logic |
| [results](https://context-fabric.ai/docs/api/cfabric/results) | Rich result types for the API |
| [search](https://context-fabric.ai/docs/api/cfabric/search) | Guidance for searching |
| [storage](https://context-fabric.ai/docs/api/cfabric/storage) | Low-level storage backends |
| [types](https://context-fabric.ai/docs/api/cfabric/types) | Type definitions |
| [utils](https://context-fabric.ai/docs/api/cfabric/utils) | Utility modules |
