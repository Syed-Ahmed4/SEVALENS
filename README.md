# SevaLens

NPU-powered offline multilingual document assistant for Snapdragon® PCs.

Scan an ID or form, read it with on-device OCR (English, Hindi, Urdu, Telugu), extract and validate key fields, and autofill an application form. Nothing leaves the laptop.

## Why it is built this way
- **Thermals and battery:** model inference runs on the Hexagon NPU with quantized models, keeping the CPU near idle.
- **No emulation:** native ARM64 Python and ONNX Runtime (QNN execution provider); no x86 dependencies.
- **Short CPU bursts avoided:** pages are batched onto the NPU; the CPU handles only UI and file I/O.

## Setup (Windows on Snapdragon)
1. Install ARM64 Python 3.x.
2. `pip install -r requirements.txt`
3. Download the quantized models listed in `models/README.md`.
4. `python app.py`

## Performance targets (not yet measured)
| Metric | Design target |
|---|---|
| Latency per page | 1 s or less |
| NPU share of inference | 90% or more of ops |
| CPU load during inference | Under 15% |
| Throttling over 10 min | None expected |
| OCR character error rate | 5% or less |

These are goals. Measured results will replace this table after validation on Snapdragon hardware.

## Demo
Add screenshots or a GIF here.

## Author
Syed Ahmed
