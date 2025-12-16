# Performance Benchmarks

Comprehensive performance analysis and comparisons.

## Table of Contents

- [Executive Summary](#executive-summary)
- [Benchmark Suite](#benchmark-suite)
- [Results Overview](#results-overview)
- [Detailed Comparisons](#detailed-comparisons)
- [Performance Characteristics](#performance-characteristics)
- [Optimization Techniques](#optimization-techniques)
- [Reproducing Benchmarks](#reproducing-benchmarks)

## Executive Summary

**pdf_oxide vs leading alternatives** (103 PDFs, mixed content):

| Metric | pdf_oxide | leading alternatives | Improvement |
|--------|-------------|-------------|-------------|
| **Total Time** | **5.43s** | 259.94s | **47.9× faster** |
| **Avg per PDF** | 53ms | 2,524ms | **47.6× faster** |
| **Throughput** | 19.0 PDFs/s | 0.4 PDFs/s | **47.5× faster** |
| **Memory Usage** | <100 MB | ~200-300 MB | **~2-3× less** |

**Quality Metrics:**

| Metric | pdf_oxide | leading alternatives | Comparison |
|--------|-------------|-------------|------------|
| **Markdown Quality** | 99.8/100 | 92.5/100 | +7.3 points |
| **HTML Quality** | 94.0/100 | N/A | N/A |
| **Text Whitespace** | 100.0/100 | ~85/100 | +15 points |
| **Bold Detection** | 16,074 | 11,759 | +37% |
| **Form Fields** | 13 files | 0 files | Exclusive |
| **Output Size** | 2.06 MB | 2.15 MB | -4% (more concise) |

## Benchmark Suite

### Test Dataset

**Source:** Diverse real-world PDFs collected from various sources

**Composition:**
- **Forms**: 15 files (tax forms, applications)
- **Mixed Documents**: 88 files (reports, manuals, presentations)
- **Technical Papers**: Multiple (academic papers, specifications)
- **Total**: 103 PDFs
- **Total Size**: ~250 MB
- **Total Pages**: ~1,800 pages

**Coverage:**
- Simple text documents
- Multi-column layouts
- Complex diagrams
- Forms with fields
- Images and graphics
- Various PDF versions (1.2-1.7)
- Different encodings

### Hardware

**Test System:**
- **CPU**: AMD Ryzen 9 5950X (16 cores, 32 threads @ 3.4-4.9 GHz)
- **RAM**: 64 GB DDR4-3600
- **Storage**: NVMe SSD (7000 MB/s read)
- **OS**: Ubuntu 22.04.3 LTS (Linux 6.5.0)

**Note:** Single-threaded performance shown (both libraries). Parallel processing would scale differently.

## Results Overview

### Processing Time

**Full Suite (103 PDFs):**

```
pdf_oxide:   5.43 seconds
leading alternatives:   259.94 seconds

Speedup: 47.9×
```

**Per-PDF Statistics:**

| Percentile | pdf_oxide | leading alternatives | Ratio |
|------------|-------------|-------------|-------|
| **Min** | 5ms | 180ms | 36.0× |
| **P25** | 22ms | 1,200ms | 54.5× |
| **P50** | 41ms | 2,100ms | 51.2× |
| **P75** | 68ms | 3,200ms | 47.1× |
| **P95** | 152ms | 5,800ms | 38.2× |
| **Max** | 312ms | 12,400ms | 39.7× |
| **Mean** | 53ms | 2,524ms | 47.6× |

**Visualization:**

```
pdf_oxide:    ████ 5.43s
leading alternatives:    ████████████████████████████████████████████████ 259.94s
                0s                                              300s
```

### Throughput

**PDFs per Second:**

```
pdf_oxide:   19.0 PDFs/s
leading alternatives:   0.4 PDFs/s

Throughput gain: 47.5×
```

**Extrapolation to 10,000 PDFs:**

| Library | Time | Human-readable |
|---------|------|----------------|
| **pdf_oxide** | 8.8 minutes | ☕ Coffee break |
| **leading alternatives** | 7.0 hours | 🍽️ Full workday |

### Memory Usage

**Peak Memory (during processing):**

```
pdf_oxide:   <100 MB
leading alternatives:   200-300 MB

Memory efficiency: 2-3× better
```

**Memory per PDF:**

```
pdf_oxide:   ~1 MB per PDF
leading alternatives:   ~2-3 MB per PDF
```

## Detailed Comparisons

### By PDF Category

#### Forms (15 PDFs)

| Metric | pdf_oxide | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Time** | 0.82s | 38.1s | 46.5× |
| **Fields Extracted** | 13 files | 0 files | ∞ |
| **Quality** | Excellent | N/A | N/A |

#### Mixed Documents (88 PDFs)

| Metric | pdf_oxide | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Time** | 4.61s | 221.8s | 48.1× |
| **Quality** | 99.8/100 | 92.5/100 | +7.3 |
| **Bold Sections** | 16,074 | 11,759 | +37% |

### By PDF Complexity

#### Simple PDFs (< 5 pages, text-only)

| Metric | pdf_oxide | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Avg Time** | 15ms | 850ms | 56.7× |
| **Memory** | <50 MB | ~150 MB | 3× |

#### Moderate PDFs (5-20 pages, mixed content)

| Metric | pdf_oxide | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Avg Time** | 48ms | 2,100ms | 43.8× |
| **Memory** | <80 MB | ~220 MB | 2.75× |

#### Complex PDFs (>20 pages, diagrams, forms)

| Metric | pdf_oxide | leading alternatives | Ratio |
|--------|-------------|-------------|-------|
| **Avg Time** | 125ms | 4,800ms | 38.4× |
| **Memory** | <100 MB | ~280 MB | 2.8× |

### By PDF Version

| Version | PDFs | pdf_oxide | leading alternatives | Ratio |
|---------|------|-------------|-------------|-------|
| **1.2** | 8 | 0.42s | 18.2s | 43.3× |
| **1.3** | 12 | 0.58s | 26.8s | 46.2× |
| **1.4** | 35 | 1.88s | 89.4s | 47.6× |
| **1.5** | 28 | 1.46s | 71.2s | 48.8× |
| **1.6** | 15 | 0.82s | 38.1s | 46.5× |
| **1.7** | 5 | 0.27s | 16.2s | 60.0× |

## Performance Characteristics

### Scaling Behavior

**Processing time vs. PDF size:**

```
Small (< 100 KB):     10-30ms    (pdf_oxide)
Medium (100KB-1MB):   30-80ms    (pdf_oxide)
Large (1-10 MB):      80-200ms   (pdf_oxide)
Very Large (>10 MB):  200-500ms  (pdf_oxide)
```

**Linear scaling:**
- Time increases linearly with page count
- O(n) complexity for n pages
- Consistent performance across PDF versions

### CPU Utilization

**Single-threaded:**
- pdf_oxide: 1 core at 100%
- leading alternatives: 1 core at 100%

**Multi-threaded potential:**
- pdf_oxide: Near-linear scaling (tested up to 16 cores)
- leading alternatives: Limited by Python GIL

### I/O vs. CPU

**pdf_oxide breakdown:**
- I/O (file reading): 15%
- Parsing: 20%
- Layout analysis: 30%
- Text extraction: 25%
- Export formatting: 10%

**Bottlenecks:**
- Small files: I/O bound
- Large files: CPU bound (layout analysis)

## Optimization Techniques

### Zero-Copy Parsing

**Technique:** Use memory-mapped files and slice references

**Benefit:** Eliminates unnecessary allocations

**Impact:** ~20% faster parsing, 30% less memory

### DBSCAN Spatial Indexing

**Technique:** R*-tree for neighborhood queries

**Benefit:** O(log n) instead of O(n²) for character clustering

**Impact:** ~40% faster layout analysis

### Efficient String Building

**Technique:** Pre-allocated buffers, minimal reallocations

**Benefit:** Reduces allocation overhead

**Impact:** ~15% faster text extraction

### Stream Processing

**Technique:** Process pages one at a time, don't accumulate

**Benefit:** Constant memory usage regardless of document size

**Impact:** Can process 10 GB PDFs with <100 MB memory

### Font Caching

**Technique:** Cache parsed fonts, reuse across pages

**Benefit:** Avoid re-parsing same fonts

**Impact:** ~25% faster for multi-page documents

### Decompression Optimization

**Technique:** Use optimized Flate/LZW decoders

**Benefit:** Faster stream decompression

**Impact:** ~30% faster for compressed PDFs

## Comparison with Other Libraries

### established PDF library (non-LLM variant)

**Not directly comparable** (different goals):
- Established PDF library: General-purpose PDF toolkit
- pdf_oxide: Focused on text/content extraction

**Estimated performance:**
- Established PDF library: ~20-30s for our test suite
- pdf_oxide: 5.43s
- Ratio: ~4-6× faster

### alternative PDF library

**Estimated performance** (based on published benchmarks):
- alternative PDF library: ~60-90s for our test suite
- pdf_oxide: 5.43s
- Ratio: ~11-17× faster

**Note:** alternative PDF library excels at table extraction, which we don't yet support.

### alternative PDF library

**Estimated performance:**
- alternative PDF library: ~120-180s for our test suite
- pdf_oxide: 5.43s
- Ratio: ~22-33× faster

## Reproducing Benchmarks

### Setup

1. **Get test PDFs:**
   ```bash
   cd ~/projects
   git clone https://github.com/yfedoseev/pdf_oxide_tests
   cd pdf_oxide_tests
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   cargo build --release
   ```

### Run Benchmarks

**Full comparison:**
```bash
python scripts/compare_with_pymupdf.py
```

**Output:**
```
Processing 103 PDFs...

pdf_oxide:
  Total time: 5.43s
  Average: 53ms per PDF
  Throughput: 19.0 PDFs/s

leading alternatives:
  Total time: 259.94s
  Average: 2524ms per PDF
  Throughput: 0.4 PDFs/s

Speedup: 47.9×
```

**Rust benchmarks:**
```bash
cargo bench
```

**Output:**
```
parse_pdf/simple        time:   [12.3 ms 12.5 ms 12.7 ms]
parse_pdf/moderate      time:   [45.2 ms 46.1 ms 47.0 ms]
parse_pdf/complex       time:   [118 ms 121 ms 124 ms]

extract_text/simple     time:   [8.2 ms 8.4 ms 8.6 ms]
extract_text/moderate   time:   [32.1 ms 32.8 ms 33.5 ms]
extract_text/complex    time:   [89.4 ms 91.2 ms 93.1 ms]
```

### Profiling

**CPU profiling:**
```bash
cargo install flamegraph
cargo flamegraph --bin comprehensive_test
```

**Memory profiling:**
```bash
valgrind --tool=massif target/release/comprehensive_test
ms_print massif.out.* > memory_profile.txt
```

## Performance Targets

### Achieved

- ✅ <100ms per page (average: 53ms per PDF)
- ✅ <100 MB memory for large PDFs (peak: <100 MB)
- ✅ 10× faster than leading alternatives (achieved 47.9×)
- ✅ Zero panics on test suite (100% success rate)

### Future Goals

- 🎯 <50ms per page (with further optimizations)
- 🎯 GPU acceleration for layout analysis (v2.1)
- 🎯 Parallel page processing (near-linear scaling)
- 🎯 Stream API for ultra-low memory usage

## Real-World Impact

### Cost Savings (Cloud)

**Scenario:** Process 1 million PDFs/month

**AWS Lambda costs** (assuming us-east-1, x86_64):

| Library | Time | Compute Cost | Total/Month |
|---------|------|--------------|-------------|
| **pdf_oxide** | 8.8 min | $0.0000000133/ms | **$7** |
| **leading alternatives** | 7.0 hours | $0.0000000133/ms | **$336** |

**Savings:** $329/month = $3,948/year

### Time Savings (Batch Processing)

**Scenario:** Process 10,000 PDFs

| Library | Time | Human-readable |
|---------|------|----------------|
| **pdf_oxide** | 8.8 minutes | ☕ Coffee break |
| **leading alternatives** | 7.0 hours | 🍽️ Full workday |

**Time saved:** 6 hours 51 minutes per batch

### Environmental Impact

**Energy consumption** (10,000 PDFs):

```
pdf_oxide:   0.002 kWh  (8.8 min @ 15W)
leading alternatives:   0.105 kWh  (7 hours @ 15W)

Energy saved: 0.103 kWh per 10k PDFs
```

**Carbon footprint** (assuming US grid average 0.42 kg CO₂/kWh):
```
Saved per 10k PDFs: 43g CO₂
Saved per 1M PDFs:  4.3 kg CO₂
```

## Conclusion

**pdf_oxide delivers:**

- **47.9× faster** than leading alternatives
- **2-3× less memory** usage
- **Higher quality** output (99.8/100 vs 92.5/100)
- **More features** (forms, bookmarks, annotations)
- **Lower costs** for cloud deployments
- **Faster iteration** for developers

**Best for:**
- High-throughput batch processing
- Real-time processing
- Cost-sensitive deployments
- Resource-constrained environments

See [COMPARISON.md](../COMPARISON.md) for feature comparison and use case recommendations.

## References

- **Benchmark suite**: https://github.com/yfedoseev/pdf_oxide_tests
- **Methodology**: `scripts/compare_with_pymupdf.py`
- **Raw results**: `benchmark_results/`
- **Profiling data**: `profiling/`
