"""SevaLens prototype: offline multilingual document field extraction.

Runs fully on the local machine. Reports whether the ONNX Runtime QNN
(Snapdragon NPU) provider is available; the current OCR engine runs on CPU.
"""
import json
import time

import numpy as np
import streamlit as st
from PIL import Image, ImageOps

from extract import extract_fields

LANGS = {"English": "en", "Hindi": "hi", "Urdu": "ur", "Telugu": "te"}
FIELD_LABELS = {
    "name": "Full name",
    "date_of_birth": "Date of birth",
    "id_number_masked": "ID number (masked)",
    "phone": "Phone",
    "pin_code": "PIN code",
}

st.set_page_config(page_title="SevaLens", page_icon="🔍", layout="wide")

st.markdown(
    """
    <style>
    .hero {background:#0A1A33;color:#fff;padding:1.4rem 1.6rem;border-radius:14px;margin-bottom:1rem;}
    .hero h1 {margin:0;font-size:2.1rem;color:#fff;}
    .hero p {margin:.3rem 0 0;color:#CADCFC;}
    .pill {display:inline-block;background:#14305A;color:#fff;border-radius:999px;
           padding:.2rem .8rem;margin:.6rem .4rem 0 0;font-size:.8rem;}
    div[data-testid="stMetric"] {background:#F4F6FA;border-radius:12px;padding:.7rem 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_reader(codes):
    import easyocr
    return easyocr.Reader(list(codes), gpu=False)


def qnn_available():
    try:
        import onnxruntime as ort
        return "QNNExecutionProvider" in ort.get_available_providers()
    except Exception:
        return False


npu = qnn_available()

st.markdown(
    f"""
    <div class="hero">
      <h1>SevaLens</h1>
      <p>Offline multilingual document assistant. Scan, read, fill.</p>
      <span class="pill">100% on-device</span>
      <span class="pill">EN · HI · UR · TE</span>
      <span class="pill">{'NPU provider detected' if npu else 'Running on CPU'}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    chosen = st.multiselect("Document languages", list(LANGS), default=["English", "Hindi"])
    enhance = st.checkbox("Enhance contrast before reading", value=True)
    st.divider()
    st.caption("Privacy: images are processed in memory on this computer. Nothing is uploaded.")
    st.caption(f"QNN (NPU) provider: {'available' if npu else 'not available'}")

upload = st.file_uploader("Upload a scan or photo of an ID or form", type=["png", "jpg", "jpeg"])

if not upload:
    st.info("Choose a document image to begin. Languages and options are in the sidebar.")
elif not chosen:
    st.warning("Select at least one document language in the sidebar.")
else:
    img = Image.open(upload).convert("RGB")
    work = ImageOps.autocontrast(img) if enhance else img
    codes = tuple(sorted({"en", *[LANGS[c] for c in chosen]}))

    with st.spinner("Loading models and reading the document..."):
        reader = load_reader(codes)
        start = time.perf_counter()
        results = reader.readtext(np.array(work))
        elapsed = time.perf_counter() - start

    lines = [text for _, text, _ in results]
    confs = [float(conf) for _, _, conf in results]
    fields = extract_fields(lines)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Read time", f"{elapsed:.2f} s")
    m2.metric("Text lines", len(lines))
    m3.metric("Avg confidence", f"{(sum(confs) / len(confs) * 100):.0f}%" if confs else "n/a")
    m4.metric("Fields found", len(fields))

    tab_form, tab_text, tab_img = st.tabs(["Autofill form", "Recognized text", "Input image"])

    with tab_form:
        st.caption("Review and correct every value before using it. Blank fields need manual entry.")
        values = {}
        left, right = st.columns(2)
        for i, (key, label) in enumerate(FIELD_LABELS.items()):
            col = left if i % 2 == 0 else right
            values[key] = col.text_input(label, value=fields.get(key, ""))
        confirmed = {k: v for k, v in values.items() if v.strip()}
        st.download_button(
            "Download confirmed fields (JSON)",
            json.dumps(confirmed, indent=2, ensure_ascii=False),
            file_name="fields.json",
            mime="application/json",
            disabled=not confirmed,
        )

    with tab_text:
        if results:
            st.dataframe(
                [{"Text": t, "Confidence": round(c, 2)} for t, c in zip(lines, confs)],
                use_container_width=True,
            )
        else:
            st.info("No text was recognized. Try a clearer image or other languages.")

    with tab_img:
        st.image(work, caption="Image used for reading", use_container_width=True)
