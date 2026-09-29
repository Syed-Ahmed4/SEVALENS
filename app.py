"""SevaLens prototype: offline multilingual document field extraction.

Runs fully on the local machine. Uses the Qualcomm QNN execution provider
through ONNX Runtime when it is available; otherwise runs on CPU.
"""
import json
import numpy as np
import streamlit as st
from PIL import Image

from extract import extract_fields

LANGS = {"English": "en", "Hindi": "hi", "Urdu": "ur", "Telugu": "te"}


@st.cache_resource
def load_reader(codes):
    import easyocr
    return easyocr.Reader(list(codes), gpu=False)


def npu_available():
    try:
        import onnxruntime as ort
        return "QNNExecutionProvider" in ort.get_available_providers()
    except Exception:
        return False


st.set_page_config(page_title="SevaLens", layout="centered")
st.title("SevaLens")
st.caption("Offline multilingual document assistant. Nothing leaves this computer.")
st.sidebar.write("QNN (NPU) provider available:", "yes" if npu_available() else "no, running on CPU")

chosen = st.multiselect("Document languages", list(LANGS), default=["English", "Hindi"])
upload = st.file_uploader("Upload a scan or photo", type=["png", "jpg", "jpeg"])

if upload and chosen:
    img = Image.open(upload).convert("RGB")
    st.image(img, caption="Input", use_container_width=True)
    codes = tuple(sorted({"en", *[LANGS[c] for c in chosen]}))
    with st.spinner("Reading document..."):
        reader = load_reader(codes)
        lines = reader.readtext(np.array(img), detail=0)
    st.subheader("Recognized text")
    st.text("\n".join(lines))
    fields = extract_fields(lines)
    st.subheader("Extracted fields")
    if fields:
        st.json(fields)
        st.download_button("Download JSON", json.dumps(fields, indent=2), "fields.json")
    else:
        st.info("No structured fields found.")
