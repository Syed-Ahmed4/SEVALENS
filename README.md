# SevaLens

NPU-oriented offline multilingual document assistant for Snapdragon® PCs, built from eSeva shop workflows.

Upload a scan or photo of an ID or form, read it with on-device OCR (English, Hindi, Urdu, Telugu), and get structured, masked fields as JSON. Nothing leaves the computer.

## Current status
This is an early prototype.
- Working: local OCR (open-source EasyOCR), rule-based field extraction (date of birth, masked 12-digit ID, phone, PIN code), JSON export, and a check for the ONNX Runtime QNN (NPU) provider.
- Not yet done: exporting the OCR models to ONNX, quantizing them for the Hexagon NPU, and measuring CPU vs NPU performance on Snapdragon hardware. The prototype currently runs on CPU.

## Why the design targets Snapdragon PCs
- **Thermals and battery:** steady inference is meant to run on the NPU with quantized models, keeping the CPU near idle.
- **No emulation:** the goal is a native ARM64 build with no x86 dependencies.
- **Short CPU bursts avoided:** pages are batched so the CPU handles only UI and file I/O.

## Run it
1. Install Python 3.10 or newer.
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
4. Open the local address Streamlit prints, choose languages, upload an image.

The first run downloads the OCR models once; after that it works offline. On Windows on Snapdragon, use ARM64 Python.

## Performance targets (not yet measured)
| Metric | Design target |
|---|---|
| Latency per page | 1 s or less |
| NPU share of inference | 90% or more of ops |
| CPU load during inference | Under 15% |
| Throttling over 10 min | None expected |
| OCR character error rate | 5% or less |

These are goals. Measured results will replace this table after validation on Snapdragon hardware.

## Files
- `app.py`: Streamlit UI and OCR pipeline
- `extract.py`: field extraction and ID masking
- `requirements.txt`: dependencies

## Author
Syed Ahmed
