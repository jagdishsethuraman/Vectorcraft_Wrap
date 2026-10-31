"""VectorCraft Image Trace - Python wrapper for the VectorCraft vector engine."""

import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
from typing import Any, Dict, Optional

def _resolve_cli_path() -> str:
    """Find vectorcraft-cli binary location."""
    # 1. Environment variable override
    env_path = os.environ.get("VECTORCRAFT_CLI")
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    # 2. On system PATH
    which_path = shutil.which("vectorcraft-cli")
    if which_path:
        return which_path

    # 3. Local build target in parent developer workspace
    local_dev_path = os.path.expanduser("~/Documents/Developer/vectorcraft/target/release/vectorcraft-cli")
    if os.path.isfile(local_dev_path) and os.access(local_dev_path, os.X_OK):
        return local_dev_path

    return "vectorcraft-cli"

CLI_PATH = _resolve_cli_path()

def trace_image(
    input_path: str,
    output_path: Optional[str] = None,
    mode: str = "color",                 # "color" | "blackAndWhite" | "grayscale" | "logo"
    colors: int = 16,
    threshold: int = 128,
    ignore_white: bool = True,
    palette: str = "automatic",          # "limited" | "fullTone" | "automatic"
    paths: int = 50,
    corners: int = 50,
    noise: int = 25,
    strokes: bool = False,
    stroke_width: float = 10.0,
    shapes: bool = False,
    auto_grouping: bool = False,
    method: str = "abutting",            # "abutting" | "overlapping"
) -> Dict[str, Any]:
    """Trace a raster image to SVG using the VectorCraft engine."""
    cli_bin = _resolve_cli_path()
    if not (os.path.isfile(cli_bin) and os.access(cli_bin, os.X_OK)) and not shutil.which(cli_bin):
        raise FileNotFoundError(
            f"vectorcraft-cli binary not found. Set VECTORCRAFT_CLI environment variable or install it on PATH."
        )

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    delete_out = False
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".svg")
        os.close(fd)
        delete_out = True

    params: Dict[str, Any] = {
        "mode": mode,
        "colors": int(colors),
        "threshold": int(threshold),
        "ignoreWhite": bool(ignore_white),
        "palette": palette,
        "paths": int(paths),
        "corners": int(corners),
        "noise": int(noise),
        "strokes": bool(strokes),
        "strokeWidth": float(stroke_width),
        "shapes": bool(shapes),
        "autoGrouping": bool(auto_grouping),
        "method": method,
    }

    cmd = [
        cli_bin,
        "run",
        "--in", input_path,
        "--cmd", "select.all",
        "--cmd", "imageTrace.makeAndExpand",
        "--params", json.dumps({"params": params}),
        "--export", output_path,
    ]

    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    duration_ms = (time.perf_counter() - t0) * 1000.0

    if proc.returncode != 0:
        if delete_out and os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"vectorcraft-cli failed (exit code {proc.returncode}): {proc.stderr or proc.stdout}")

    # Parse JSON output steps from vectorcraft-cli
    stats = {"anchors": 0, "colors": 0, "paths": 0, "warnings": []}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("command") == "imageTrace.makeAndExpand":
                res = data.get("result", {})
                stats["anchors"] = res.get("anchors", 0)
                stats["colors"] = res.get("colors", 0)
                stats["paths"] = res.get("paths", 0)
                stats["warnings"] = res.get("warnings", [])
        except Exception:
            pass

    svg_content = ""
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        if delete_out:
            os.remove(output_path)

    return {
        "svg": svg_content,
        "stats": stats,
        "duration_ms": round(duration_ms, 2),
        "output_path": output_path if not delete_out else None,
    }

def trace_base64(
    data_uri: str,
    **kwargs
) -> Dict[str, Any]:
    """Trace an image provided as a base64 Data URI."""
    if "," in data_uri:
        header, b64_str = data_uri.split(",", 1)
        ext = ".png"
        if "jpeg" in header or "jpg" in header:
            ext = ".jpg"
        elif "webp" in header:
            ext = ".webp"
    else:
        b64_str = data_uri
        ext = ".png"

    img_bytes = base64.b64decode(b64_str)
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_in:
        tmp_in.write(img_bytes)
        tmp_in_path = tmp_in.name

    try:
        return trace_image(tmp_in_path, **kwargs)
    finally:
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)
