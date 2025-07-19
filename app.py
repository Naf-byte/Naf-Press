# app.py
import io
import requests
from PIL import Image
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.utils import ImageReader

# --- Page Config ---
st.set_page_config(
    page_title="Image → PDF Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
:root {
  --primary-color: #0052cc;
  --accent-color: #ffac33;
  --bg-color: #f5f7fa;
  --card-bg: #ffffff;
  --text-color: #333333;
}

body, .block-container {
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: 'Segoe UI', sans-serif;
}

/* Header */
.header {
  background-color: var(--primary-color);
  color: white;
  padding: 1.5rem 2rem;
  border-radius: 8px;
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  animation: fadeInDown 1s ease-out forwards;
}

/* Sidebar background & black right border */
[data-testid="stSidebar"] {
  background-color: var(--card-bg);
  border-right: 4px solid #000;
  padding: 1.5rem;
  animation: fadeInLeft 1s ease-out forwards;
}

/* Entire Settings form wrapper */
[data-testid="stSidebar"] > form {
  border: 2px solid #000;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  background: var(--card-bg);
}

/* Always-black borders on the individual widgets */
[data-testid="stSidebar"] > form .stSelectbox,
[data-testid="stSidebar"] > form .stSlider,
[data-testid="stSidebar"] > form .stTextInput {
  border: 2px solid #000 !important;
  border-radius: 6px !important;
  padding: 0.35rem !important;
  margin-bottom: 1rem !important;
}

/* Remove default focus outline/box-shadow */
[data-testid="stSidebar"] > form .stSelectbox * ,
[data-testid="stSidebar"] > form .stSlider * ,
[data-testid="stSidebar"] > form .stTextInput * {
  outline: none !important;
  box-shadow: none !important;
}

/* Tab‐content cards */
.tab-content {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  animation: fadeInUp 0.8s ease-out forwards;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.tab-content:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

/* Buttons */
.stButton>button, .downloadButton>button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  transition: background-color 0.2s ease, transform 0.2s ease;
}
.stButton>button:hover, .downloadButton>button:hover {
  background-color: var(--accent-color);
  transform: scale(1.05);
}

/* Footer */
.footer {
  text-align: center;
  color: #666666;
  margin-top: 3rem;
  font-size: 0.85rem;
}

/* Animations */
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='header'>Image to PDF Converter</div>", unsafe_allow_html=True)

# --- Sidebar Settings ---
with st.sidebar:
    st.header("Settings")
    page_size = st.selectbox("Page Size", ["A4", "Letter"])
    dpi = st.slider("Target DPI", 72, 600, 150, help="Higher DPI → larger PDF & finer print detail")
    output_name = st.text_input("Output filename", "converted.pdf")
    st.markdown("")  # force form to render
    # st.caption("Built with ❤️ Streamlit • Pillow • ReportLab")

# --- PDF Generation Logic ---
PAGE_SIZES = {"A4": A4, "Letter": letter}
page_w_pt, page_h_pt = PAGE_SIZES[page_size]

def make_pdf(pil_images):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w_pt, page_h_pt))
    for img in pil_images:
        img = img.convert("RGB")
        iw, ih = img.size

        target_px_w = int(page_w_pt * dpi / 72)
        target_px_h = int(page_h_pt * dpi / 72)
        scale = min(target_px_w / iw, target_px_h / ih)

        new_w_px = int(iw * scale)
        new_h_px = int(ih * scale)
        img_resized = img.resize((new_w_px, new_h_px), Image.LANCZOS)

        w_pt = new_w_px * 72.0 / dpi
        h_pt = new_h_px * 72.0 / dpi
        x = (page_w_pt - w_pt) / 2
        y = (page_h_pt - h_pt) / 2

        reader = ImageReader(img_resized)
        c.drawImage(reader, x, y, width=w_pt, height=h_pt)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf

# --- Tabs for Input ---
tabs = st.tabs(["📁 Local Images", "🟦 Local WebP", "🌐 Image URLs"])

# Local Images Tab
with tabs[0]:
    # st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("""
        <div class='tab-content'>
        <p style="font-size:1.1rem; margin-bottom:1rem;">
            Select one or more images (PNG, JPEG, TIFF, GIF, BMP) from your computer—
      drag & drop or browse below—and then click “Generate PDF” to compile them
      into a single high-quality PDF document.
        </p>
        </div>
    """, unsafe_allow_html=True)
    st.subheader("Upload PNG / JPEG / TIFF / GIF / BMP")
    files = st.file_uploader("Select image files",
                             type=["png","jpg","jpeg","bmp","gif","tiff"],
                             accept_multiple_files=True,
                             label_visibility="collapsed", key="imgs")
    if files and st.button("Generate PDF", key="gen1"):
        pil_imgs = [Image.open(f) for f in files]
        pdf_buf = make_pdf(pil_imgs)
        size_kb = len(pdf_buf.getvalue()) // 1024
        st.success(f"Created **{output_name}** — {size_kb} KB at {dpi} DPI")
        st.download_button("Download PDF", pdf_buf, file_name=output_name, mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# WebP Tab
with tabs[1]:
    st.markdown("""
        <div class='tab-content'>
        <p style="font-size:1.1rem; margin-bottom:1rem;">
            Select one or more images (WEBP) from your computer—
      drag & drop or browse below—and then click “Generate PDF” to compile them
      into a single high-quality PDF document.
        </p>
        </div>
    """, unsafe_allow_html=True)
    st.write("**Upload any WebP image to convert into PDF**")
    st.subheader("Upload WebP Files")
    files = st.file_uploader("Select .webp files",
                             type=["webp"],
                             accept_multiple_files=True,
                             label_visibility="collapsed", key="webp")
    if files and st.button("Generate PDF", key="gen2"):
        pil_imgs = [Image.open(f) for f in files]
        pdf_buf = make_pdf(pil_imgs)
        size_kb = len(pdf_buf.getvalue()) // 1024
        st.success(f"Created **{output_name}** — {size_kb} KB at {dpi} DPI")
        st.download_button("Download PDF", pdf_buf, file_name=output_name, mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# URLs Tab
with tabs[2]:
    st.markdown("""
        <div class='tab-content'>
        <p style="font-size:1.1rem; margin-bottom:1rem;">
            Copy link of image and Paste the it below then click “Generate PDF” to compile them
      into a single high-quality PDF document.
        </p>
        </div>
    """, unsafe_allow_html=True)
    st.subheader("Convert Online Image URLs to PDF")
    text = st.text_area("Enter URLs (one per line)",
                        placeholder="https://nafbyte.com/image1.png\nhttps://…",
                        label_visibility="collapsed")
    if text.strip() and st.button("Generate PDF", key="gen3"):
        urls = [u.strip() for u in text.splitlines() if u.strip()]
        imgs, errs = [], []
        for u in urls:
            try:
                r = requests.get(u, timeout=10); r.raise_for_status()
                imgs.append(Image.open(io.BytesIO(r.content)))
            except Exception as e:
                errs.append(f"`{u}` → {e}")
        if errs:
            st.error("❌ The provided URL does not point to an image.\n\n"
            f"Please supply a direct image link ending with one of .png, .jpg, .jpeg, .bmp, .gif, .tiff, .webp")
        if imgs:
            pdf_buf = make_pdf(imgs)
            size_kb = len(pdf_buf.getvalue()) // 1024
            st.success(f"Created **{output_name}** — {size_kb} KB at {dpi} DPI")
            st.download_button("Download PDF", pdf_buf, file_name=output_name, mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2025 Naf-Byte — Nafay UrRehman</div>", unsafe_allow_html=True)



# # app.py
# import io
# import os
# from PIL import Image
# import streamlit as st

# # --- Page setup ---
# st.set_page_config(
#     page_title="🖼️→📄 Image to PDF",
#     layout="centered",
#     initial_sidebar_state="expanded",
# )

# # --- Sidebar options ---
# st.sidebar.header("Settings")
# page_size = st.sidebar.selectbox("Page size", ["A4", "Letter"])
# dpi = st.sidebar.slider("Resolution (DPI)", 72, 300, 150, help="Higher DPI → larger file & sharper images")
# output_name = st.sidebar.text_input("Output filename", value="converted.pdf")

# # Compute canvas size in pixels
# if page_size == "A4":
#     mm_w, mm_h = 210, 297
# else:  # Letter
#     mm_w, mm_h = 216, 279

# # mm to inches: 1 in = 25.4 mm
# inch_w = mm_w / 25.4
# inch_h = mm_h / 25.4
# PAGE_W = int(inch_w * dpi)
# PAGE_H = int(inch_h * dpi)

# # --- App UI ---
# st.title("🖼️→📄 Image to PDF Converter")
# st.write("1. Upload one or more images.  2. Click **Generate PDF**.  3. Download your PDF.")

# uploaded_files = st.file_uploader(
#     "Upload image files",
#     type=["png", "jpg", "jpeg", "bmp", "gif", "tiff"],
#     accept_multiple_files=True
# )

# if uploaded_files:
#     st.markdown("**Preview:**")
#     cols = st.columns( min(4, len(uploaded_files)) )
#     for idx, file in enumerate(uploaded_files):
#         cols[idx % len(cols)].image(file, use_column_width=True)

#     if st.button("🛠️ Generate PDF"):
#         pages = []
#         for file in uploaded_files:
#             img = Image.open(file).convert("RGB")
#             iw, ih = img.size
#             # scale to fit
#             scale = min(PAGE_W / iw, PAGE_H / ih)
#             nw, nh = int(iw * scale), int(ih * scale)
#             img_resized = img.resize((nw, nh), Image.LANCZOS)
#             # center on blank page
#             page = Image.new("RGB", (PAGE_W, PAGE_H), (255, 255, 255))
#             x = (PAGE_W - nw) // 2
#             y = (PAGE_H - nh) // 2
#             page.paste(img_resized, (x, y))
#             pages.append(page)

#         # Save to in-memory buffer
#         buffer = io.BytesIO()
#         pages[0].save(
#             buffer,
#             format="PDF",
#             save_all=True,
#             append_images=pages[1:],
#             resolution=dpi
#         )
#         buffer.seek(0)

#         st.success(f"Generated **{output_name}** ({len(pages)} page{'s' if len(pages)>1 else ''})")
#         st.download_button(
#             label="📥 Download PDF",
#             data=buffer,
#             file_name=output_name,
#             mime="application/pdf"
#         )
# else:
#     st.info("Upload at least one image to get started.")

# # --- Footer ---
# st.markdown("---")
# st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) & Pillow")
