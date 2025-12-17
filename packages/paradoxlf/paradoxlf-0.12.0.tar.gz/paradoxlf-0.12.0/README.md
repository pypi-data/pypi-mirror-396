# Paradox: Latent Memory & Simulation Engine

**Paradox** is a lightweight, hardware-agnostic cognitive architecture for AI agents. It provides a dynamic "Latent Memory" that doesn't just store data but allows for active simulation, evolution, and reasoning.

## 🎯 The Main Point
**"Extreme Efficiency through Abstraction."**

We have too much data and not enough hardware. Paradox solves this by replacing heavy "Real Objects" with lightweight "Latent Vectors", allowing you to perform Supercomputer-scale tasks on a Laptop.

*   **Don't store the Cake** (100MB Object).
*   **Store the Recipe** (1KB Vector).
*   **Bake it on demand.**

## 🚀 Key Features

*   **Multimodal Intelligence (v0.7.0):** Unified encoding for Images and Text using CLIP.
*   **Semantic Proximity (v0.8.0):** Weighted "Attention" search to prioritize specific features (e.g., Color vs Shape).
*   **Latent Reasoning (v0.9.0):** Perform concept arithmetic (`King - Man + Woman = Queen`) directly in vector space.
*   **Temporal Intelligence (v0.10.0):** Track thought trajectories and predict future states.
*   **Intelligence APIs (v0.11.0):** High-level methods like `imagine()`, `predict_future()`, and `conceptual_search()`.
*   **Hybrid Compute:** Automatically runs on **GPU (PyTorch)** if available, gracefully falls back to **CPU (NumPy/MMap)**.

## 📦 Installation

```bash
git clone https://github.com/ethcocoder/paradoxlf.git
cd paradoxlf
pip install .[ai,ui]
```

## ⚡ Quick Start: Intelligence Layer

```python
from paradox.engine import LatentMemoryEngine
from paradox.media.clip_module import CLIPEncoder

# 1. Initialize the Brain
encoder = CLIPEncoder() # Loads CLIP Model
engine = LatentMemoryEngine(dimension=encoder.dimension)
engine.set_encoder(encoder)

# 2. Learn Concepts
engine.add("Telephone", {"name": "Telephone"})
engine.add("Computer", {"name": "Computer"})
engine.add("Smartphone", {"name": "Smartphone"})

# 3. Imagine New Concepts (Blending)
# What is half phone, half computer?
new_idea = engine.imagine("Telephone", "Computer", ratio=0.5)

# 4. Search for Meaning
results = engine.conceptual_search(new_idea, k=1)
print(f"Imagined Concept is closest to: {results[0][2]['name']}")
```

## 🧠 Advanced Capabilities

### 1. Temporal Prediction (Forecasting)
Predict where a sequence of thoughts or video frames is heading.
```python
history = [vector_t0, vector_t1, vector_t2]
future_vector = engine.predict_future(history, steps=1)
```

### 2. Semantic Search with Attention
Search for "Red Car", but tell the engine that Color is 10x more important than Shape.
```python
weights = [10.0, 1.0, ...] # Heavy weight on first dimensions
results = engine.query(query_vec, weights=weights)
```

### 3. Visual Dashboard
Explore your memory space interactively.
```bash
streamlit run paradox/ui/dashboard.py
```

## 🌍 Innovation Impact

Paradox is a fundamental engine for **Massive Scale Simulation**:

| Domain | Problem | Paradox Solution |
| :--- | :--- | :--- |
| **Cognitive AI** | LLMs are stateless/expensive. | Paradox provides a cheap, evolvable long-term memory. |
| **Scientific Sim** | Simulating millions of particles is slow. | Latent physics allows interacting with millions of entities. |
| **Big Data** | Searching billions of logs is slow. | Proximity search finds anomalies instantly (O(1) approx). |

## 🤝 Contributing
Open source contributions are welcome. Please submit a PR for review.

## 📄 License
MIT License