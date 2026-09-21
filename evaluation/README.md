# Retrieval Evaluation

## Dataset

30 section-level questions covering:

- risks
- business
- industry
- IPO
- financial information

## Results

Dense BGE-M3
Recall@5    0.633
Precision@5 0.173
MRR         0.398

Hybrid + hierarchy + query expansion
Recall@5    0.967
Precision@5 0.713
MRR         0.864

## Reranker Experiment

A cross-encoder reranker was evaluated but rejected because
it degraded retrieval quality on the benchmark.

## Notes

These results are internal engineering benchmarks on a
30-question section-level evaluation set. They should not
be presented as production-quality evaluation claims.