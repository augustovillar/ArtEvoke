# Qdrant Testing - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd /home/augustovillar/ArtEvoke/project_assets/tests/qdrant
pip install -r requirements.txt
```

**Note:** The scripts will automatically download the embedding model to `model_cache/` folder (local cache to avoid permission issues)

### Step 2: Start Qdrant (Docker mode)
```bash
docker-compose up -d
```

Wait ~10 seconds for Qdrant to initialize, then verify it's running:
```bash
curl http://localhost:6333/
```

### Step 3: Run the Test

**For paper plots with multiple configurations (recommended):**
```bash
python testQdrant_multiple_configs.py local
```

**For quick single-config test:**
```bash
python testQdrant.py local
```

Expected runtime: 
- Single config: ~5-10 minutes
- Multi-config: ~15-25 minutes (tests 3 configurations × 4 dataset sizes)

---

## 📊 Understanding Results

The test will output a table like:

```
Index  Latency (s/query)  Upload Time (s)  Memory (MB)  Recall@1  Recall@3  Recall@6  # Samples  m   ef_construct
HNSW   0.002543          12.45            2156.78      0.998     1.000     1.000     1000       16  100
HNSW   0.003122          58.32            10783.89     0.997     0.999     1.000     5000       16  100
...
```

**Key Metrics:**
- **Latency**: How fast each query runs (lower is better)
  - Target: < 50ms for web applications
  - Qdrant (Docker): includes ~1-5ms network overhead
- **Recall@K**: Accuracy - how often the correct image is in top-K results
  - Target: > 0.95 (95%)
- **Memory**: Storage required for vectors + index
- **Upload Time**: One-time cost to populate the database

---

## 🔄 Compare with FAISS

After running Qdrant tests, compare with FAISS:

```bash
# Run FAISS tests (if not done already)
cd ../faiss
python testFaiss.py cpu

# Return to Qdrant directory and compare
cd ../qdrant
python compare_results.py
```

This will show:
- Latency comparison across systems
- Network overhead analysis
- Recall vs speed trade-offs

---

## 🧪 Testing Modes

### Local Mode (Production-like)
```bash
python testQdrant.py local
```
- Uses Docker container
- Includes REST API network overhead
- Most realistic for production deployment

### Memory Mode (Development)
```bash
python testQdrant.py memory
```
- No Docker required
- No network overhead
- Faster for development/iteration

---

## 🎯 For Your Paper (LaTeX Plots)

To generate data for plots like your FAISS figures:

### Step 1: Run Multi-Config Test
```bash
python testQdrant_multiple_configs.py local
```

### Step 2: Get TikZ Coordinates

The script automatically prints LaTeX TikZ coordinates at the end:

```
LATEX TIKZ COORDINATES
======================

% Recall@1 coordinates:
\addplot[color=blue, mark=*] coordinates {(1, 0.998) (5, 0.996) ...};
\addlegendentry{HNSW-High-Recall}
...
```

### Step 3: Create Your Figure

Copy the coordinates into your LaTeX document to create plots similar to Figure~\ref{fig:faiss_gpu_sidebyside}:

```latex
\begin{figure}[H]
\centering
\begin{subfigure}[t]{0.49\textwidth}
\begin{tikzpicture}
\begin{axis}[
    ylabel={Recall@1},
    xlabel={Number of Samples ($\cdot 10^3$)},
    title={Recall@1 (Qdrant HNSW)},
    ...
]
% PASTE YOUR RECALL@1 COORDINATES HERE
\end{axis}
\end{tikzpicture}
\end{subfigure}
...
\end{figure}
```

### Step 4: Text for Results Section

Example text template:

```
The average query latency for Qdrant HNSW-Balanced (m=16, ef_construct=100) 
was X.XX ms for the 15,000-vector collection, compared to Y.YY ms for 
FAISS IndexFlatIP. This modest increase includes REST API network overhead 
(~Z ms) rather than the vector search itself.

Recall metrics remained highly competitive across configurations:
- HNSW-High-Recall: Recall@1 = 0.XXX (comparable to FAISS Flat)
- HNSW-Balanced: Recall@1 = 0.XXX (good speed/accuracy trade-off)
- HNSW-Fast: Recall@1 = 0.XXX (prioritizes speed)

Figure~\ref{fig:qdrant_performance} shows the performance trade-offs 
across dataset sizes and HNSW parameters, demonstrating that Qdrant 
remains well within interactive requirements (<50ms) while providing 
production-ready features like metadata filtering, persistence, and 
horizontal scaling.
```

### Step 5: Compare with FAISS
```bash
python compare_results.py
```

---

## 🐛 Troubleshooting

**"Connection refused" error:**
```bash
# Check if Docker container is running
docker ps | grep qdrant

# View logs
docker-compose logs qdrant

# Restart if needed
docker-compose restart
```

**Port 6333 already in use:**
```bash
# Find what's using the port
sudo lsof -i :6333

# Stop existing Qdrant
docker stop qdrant_test
```

**Out of memory:**
```bash
# Edit testQdrant.py and reduce subset_sizes
# For example: subset_sizes = [1000, 5000]
```

---

## 🧹 Cleanup

When finished:
```bash
# Stop Qdrant container
docker-compose down

# Remove stored data (optional)
rm -rf qdrant_storage/

# Remove cached models (optional, saves ~1.5GB)
rm -rf model_cache/

# Remove result files (optional)
rm qdrant_results_*.csv
```

