# VectorCraft Python Wrap & Trace Lab

A lightweight, high-performance Python wrapper and interactive test environment for VectorCraft's clean-room raster-to-vector tracing engine.

---

## Highlights

* **Ultra-Fast Turnaround:** Traces complex raster images to clean SVG in **~11 ms** on Apple Silicon via native VectorCraft engine.
* **Full Algorithmic Parity:**
  * **Quantization & Palette Reduction:** Black & white threshold, Grayscale (1-D k-means), and Color (median cut + weighted k-means).
  * **Sub-Pixel Edge Displacement:** Fractional anti-aliased edge alignment before Bézier fitting.
  * **Abutting Shared Boundaries:** Cuts outlines at 3-way junctions and synchronizes abutting curves so adjacent color patches have zero hairline gaps.
  * **Centerline / Line Art Extraction:** Medial-axis thinning with automatic stroke width estimation.
  * **Shape Recognition:** Live detection and snapping for circles, ellipses, rectangles, and regular polygons.
  * **Flat Logo Mode:** Automatic corner restoration and line/arc snapping.
* **Interactive Localhost Web UI:** Zero-dependency testing laboratory with live side-by-side comparison, wireframe inspection, slider telemetry, and SVG export.

---

## Architecture

```text
┌──────────────────────────┐       ┌──────────────────────────────┐
│  Python Application      │       │  Localhost Web Lab (8765)    │
│  vectorcraft_trace.py    │       │  server.py + index.html      │
└────────────┬─────────────┘       └──────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    vectorcraft-cli engine                       │
│  - Select all artboard nodes                                    │
│  - imageTrace.makeAndExpand (JSON params)                       │
│  - Export clean Bézier SVG                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quickstart

### 1. Requirements
* Python 3.8+ (standard library only; zero pip dependencies required).
* `vectorcraft-cli` binary built and available on `PATH` or pointed to by `VECTORCRAFT_CLI`.

### 2. Python Usage
```python
import vectorcraft_trace

# Basic tracing
result = vectorcraft_trace.trace_image(
    input_path="input.png",
    output_path="output.svg",
    mode="color",            # "color" | "logo" | "blackAndWhite" | "grayscale"
    colors=16,
    ignore_white=True,
    strokes=False
)

print(result["stats"])       # {'anchors': 8, 'colors': 2, 'paths': 2}
print(result["duration_ms"]) # e.g. 11.57 ms
```

### 3. Running the Test Lab
Launch the local test server:
```bash
python3 server.py
```
Open **`http://localhost:8765`** in your browser.

* Drag & drop images or click preloaded samples.
* Adjust color count, noise suppression, thresholds, and stroke width with live feedback.
* Inspect wireframe Bézier anchor points and download generated SVGs.

---

## License
MIT / Apache-2.0
