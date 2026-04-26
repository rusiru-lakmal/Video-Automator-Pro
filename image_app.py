import streamlit as st
from PIL import Image
import os
import time

# Lazy import engine to avoid crashing if ML deps not installed
try:
    from image_engine import AIImageArchitect
    ENGINE_AVAILABLE = True
except Exception:
    ENGINE_AVAILABLE = False

# ── Image Tool UI ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_engine():
    return AIImageArchitect()

def main():
    st.markdown('<div class="image-tool">', unsafe_allow_html=True)

    # ── Hero Banner ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner" style="background:rgba(255,255,255,0.02);">
        <div style="position:absolute;inset:0;
                    background:linear-gradient(135deg,rgba(30,140,255,0.08) 0%,transparent 60%);
                    pointer-events:none;border-radius:20px;"></div>
        <div class="hero-badge" style="background:rgba(30,140,255,0.12);
             border-color:rgba(30,140,255,0.25);color:#60a5fa;">✨ Image Suite</div>
        <h1 class="hero-title hero-title-image">AI Image Architect</h1>
        <p class="hero-sub">
            Studio-grade face restoration and 4× cinematic upscaling.
            Powered by GFPGAN + Real-ESRGAN — running locally on your hardware.
        </p>
        <div class="stats-row">
            <div class="stat-pill">Upscale <span>4× Real-ESRGAN</span></div>
            <div class="stat-pill">Face Restore <span>GFPGAN v1.4</span></div>
            <div class="stat-pill">Bokeh <span>rembg · depth mask</span></div>
            <div class="stat-pill">Output <span>4K PNG</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not ENGINE_AVAILABLE:
        st.error("⚠️  AI engine not available. Run: `pip install -r image_requirements.txt`")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Main Grid ──────────────────────────────────────────────────────────────
    left, right = st.columns([1.3, 1], gap="large")

    # ── LEFT: Upload ───────────────────────────────────────────────────────────
    with left:
        st.markdown('<div class="section-label">01 — Source Image</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card" style="padding-bottom:0;border-radius:16px 16px 0 0;border-bottom:0;">
            <div class="card-header">
                <div class="card-icon icon-blue">🖼️</div>
                <div>
                    <div class="card-title">Image Input</div>
                    <div class="card-subtitle">JPG · PNG · WEBP · Any resolution</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your image here",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="image_upload"
        )

        if uploaded_file:
            input_image = Image.open(uploaded_file).convert("RGB")
            w, h = input_image.size
            st.markdown("<br>", unsafe_allow_html=True)
            st.image(input_image, use_column_width=True)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-top:12px;
                        padding:10px 14px;background:rgba(255,255,255,0.03);
                        border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
                <span style="color:#22c55e;font-size:1.1rem;">✓</span>
                <span style="font-size:0.82rem;color:rgba(255,255,255,0.6);">
                    <strong style="color:#fff">{uploaded_file.name}</strong>
                    &nbsp;·&nbsp;{w}×{h}px &nbsp;·&nbsp;
                    {round(uploaded_file.size/1024, 0):.0f} KB
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── RIGHT: Config + Action ─────────────────────────────────────────────────
    with right:
        st.markdown('<div class="section-label">02 — Enhancement Engine</div>', unsafe_allow_html=True)

        # Sliders Card
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-blue">⚡</div>
                <div>
                    <div class="card-title">Processing Parameters</div>
                    <div class="card-subtitle">Tune the enhancement strength</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        intensity  = st.slider("Enhancement Intensity", 0.0, 1.0, 0.5, 0.05)
        brightness = st.slider("Brightness Boost ×", 0.5, 2.0, 1.0, 0.05)

        st.markdown("<br>", unsafe_allow_html=True)

        # Options Card
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-gold">🎨</div>
                <div>
                    <div class="card-title">Visual Effects</div>
                    <div class="card-subtitle">Post-processing pipeline</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bokeh = st.checkbox("📸  Portrait Bokeh (Background Blur)", value=False)

        st.markdown("""
        <div style="padding:12px 14px;background:rgba(30,140,255,0.06);
                    border:1px solid rgba(30,140,255,0.15);border-radius:10px;
                    font-size:0.78rem;color:rgba(255,255,255,0.5);margin-top:12px;">
            💡 First run downloads AI models (~500 MB). Subsequent runs are instant.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # CTA Button
        if uploaded_file:
            if st.button("✨  Enhance with Architect Mode", key="image_enhance_btn"):
                engine = load_engine()
                with st.spinner("Restoring faces & upscaling to 4K…"):
                    t0 = time.time()
                    try:
                        result = engine.enhance(
                            input_image,
                            intensity=intensity,
                            bokeh=bokeh,
                            brightness=brightness
                        )
                        elapsed = time.time() - t0

                        st.balloons()
                        st.success(f"✅  Enhanced in {elapsed:.1f}s — ready to download!")

                        # Show result
                        st.markdown('<div class="section-label" style="margin-top:28px;">03 — Result</div>',
                                    unsafe_allow_html=True)
                        st.image(result, use_column_width=True)

                        from io import BytesIO
                        buf = BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            "📥  Download 4K PNG",
                            data=buf.getvalue(),
                            file_name="architect_enhanced.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"Engine error: {e}")
        else:
            st.button("✨  Enhance with Architect Mode", disabled=True, key="image_enhance_btn_disabled")

    st.markdown('</div>', unsafe_allow_html=True)  # close .image-tool

if __name__ == "__main__":
    main()
