import streamlit as st
import os
import tempfile
from video_processor import process_video

# ── Video Tool UI ─────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="video-tool">', unsafe_allow_html=True)

    # ── Hero Banner ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">🎬 Video Suite</div>
        <h1 class="hero-title">Video Automator Pro</h1>
        <p class="hero-sub">
            Bypass copyright fingerprinting with military-grade AI transformations.
            Mirror, retime, regrade — in one click.
        </p>
        <div class="stats-row">
            <div class="stat-pill">Speed <span>0.5× – 2.0×</span></div>
            <div class="stat-pill">Zoom <span>1.0× – 2.0×</span></div>
            <div class="stat-pill">Modes <span>Mirror · Vivid · Cinematic</span></div>
            <div class="stat-pill">Output <span>H.264 · AAC 320k</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Main Grid ──────────────────────────────────────────────────────────────
    left, right = st.columns([1.15, 1], gap="large")

    # ── LEFT: Upload & Preview ─────────────────────────────────────────────────
    with left:
        st.markdown('<div class="section-label">01 — Media Source</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card" style="padding-bottom:0;border-bottom:0;border-radius:16px 16px 0 0;">
            <div class="card-header">
                <div class="card-icon icon-red">📁</div>
                <div>
                    <div class="card-title">Media Library</div>
                    <div class="card-subtitle">MP4 or MOV · Any resolution</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your video here, or browse",
            type=['mp4', 'mov'],
            label_visibility="collapsed",
            key="video_upload"
        )

        if uploaded_file:
            st.markdown("<br>", unsafe_allow_html=True)
            st.video(uploaded_file)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-top:12px;
                        padding:10px 14px;background:rgba(255,255,255,0.03);
                        border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
                <span style="color:#22c55e;font-size:1.1rem;">✓</span>
                <span style="font-size:0.82rem;color:rgba(255,255,255,0.6);">
                    <strong style="color:#fff">{uploaded_file.name}</strong> &nbsp;·&nbsp;
                    {round(uploaded_file.size/1024/1024, 1)} MB loaded
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── RIGHT: Controls ────────────────────────────────────────────────────────
    with right:
        st.markdown('<div class="section-label">02 — Transformation Engine</div>', unsafe_allow_html=True)

        # -- Speed & Zoom Card --
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-gold">⚡</div>
                <div>
                    <div class="card-title">Temporal Controls</div>
                    <div class="card-subtitle">Speed & spatial reframing</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        speed = st.slider("Playback Speed ×", 0.5, 2.0, 1.05, 0.01,
                          help="Shifts audio fingerprint; 1.05× is imperceptible")
        zoom  = st.slider("Zoom Level ×", 1.0, 2.0, 1.10, 0.05,
                          help="Crops edge detection patterns")

        st.markdown("<br>", unsafe_allow_html=True)

        # -- Toggles Card --
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-red">🎛️</div>
                <div>
                    <div class="card-title">Signal Processing</div>
                    <div class="card-subtitle">Copyright bypass layers</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            mirror        = st.checkbox("↔ Mirror", value=True)
            enhance       = st.checkbox("✨ AI Enhance", value=False, help="Pro-grade sharpening & detail restoration")
            cinematic     = st.checkbox("🎬 Cinematic 9:16", value=False)
        with col_b:
            color_jitter  = st.checkbox("🎨 Color Jitter", value=True)
            vivid         = st.checkbox("🌈 Vivid Mode", value=False)
            no_veo        = st.checkbox("🚫 No Veo", value=False, help="Surgical watermark removal")
            comic_style   = st.checkbox("💥 Comic Style", value=False, help="Transform video into a comic book/cartoon version")
            painterly     = st.checkbox("🎨 Painterly Style", value=False, help="Soft, hand-painted illustration style (like your sample)")
            ai_style      = st.checkbox("🤖 Real AI Style", value=False, help="EXTREMELY SLOW - Professional AI hand-drawn look (AnimeGANv2)")
        
        upscale_4k = st.checkbox("🚀 4K Ultra HD", value=False, help="Upscale to 3840x2160 using Lanczos4 interpolation")

        st.markdown("<br>", unsafe_allow_html=True)

        # -- Viral Growth Card --
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-green">📈</div>
                <div>
                    <div class="card-title">Viral Optimization</div>
                    <div class="card-subtitle">Algorithmic growth hackers</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pitch_shift = st.slider("Audio Pitch Shift", -2.0, 2.0, 0.5, 0.1, 
                                help="Slightly shifts voice/music pitch to bypass audio ID matching. 0.5 is ideal.")
        
        viral_hook = st.text_input("Viral Hook / Headline", placeholder="Wait for the end... 😱", help="A catchy headline to grab attention")
        hook_pos = st.radio("Hook Position", ["top", "bottom"], horizontal=True)

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            add_grain = st.checkbox("🎞️ Film Grain", value=True, help="Adds moving texture to bypass pixel-hashing")
            seamless_loop = st.checkbox("♾️ Seamless Loop", value=False, help="Fades the end into the start for infinite rewatching")
        with col_v2:
            clean_meta = st.checkbox("🧹 Clean Metadata", value=True, help="Strip EXIF and tracking data from file")

        st.markdown("<br>", unsafe_allow_html=True)

        # -- Render Button --
        if st.button("🚀  Process & Render", key="video_render_btn"):
            if uploaded_file is None:
                st.warning("Please upload a video first.")
            else:
                try:
                    # Automatically find the downloads directory (works on Mac and Server)
                    base_dir = os.getcwd()
                    download_dir = os.path.join(base_dir, "downloads")
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    
                    import uuid
                    unique_id = uuid.uuid4().hex[:8]
                    output_filename = f"output_{unique_id}.mp4"
                    out = os.path.join(download_dir, output_filename)

                    with tempfile.TemporaryDirectory() as tmp:
                        inp = os.path.join(tmp, "input.mp4")
                        with open(inp, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        if ai_style:
                            st.info("💡 Real AI Style is very intensive. It will take ~2 seconds per frame. A 10s video might take 15 minutes.")
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def update_progress(percent):
                            progress_bar.progress(percent)
                            status_text.text(f"Processing AI Frames: {int(percent*100)}%")

                        with st.spinner("⚙️  Initializing AI Model & Rendering..."):
                            process_video(inp, out,
                                          speed=speed, zoom=zoom,
                                          mirror=mirror, color_jitter=color_jitter,
                                          enhance_quality=enhance,
                                          vivid_mode=vivid,
                                          cinematic_mode=cinematic,
                                          remove_veo_watermark=no_veo,
                                          upscale_4k=upscale_4k,
                                          comic_style=comic_style,
                                          painterly_style=painterly,
                                          ai_style=ai_style,
                                          pitch_shift=pitch_shift,
                                          add_grain=add_grain,
                                          clean_meta=clean_meta,
                                          viral_hook=viral_hook,
                                          hook_pos=hook_pos,
                                          seamless_loop=seamless_loop,
                                          progress_callback=update_progress if ai_style else None)

                        st.balloons()
                        st.success("✅  Render complete! Your file is ready.")

                        # Direct High-Speed Download Link via Nginx (Server only)
                        download_url = f"/downloads/{output_filename}"
                        st.markdown(f"""
                            <div style="margin-top: 20px;">
                                <a href="{download_url}" download style="
                                    text-decoration: none;
                                    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                                    color: white;
                                    padding: 14px 28px;
                                    border-radius: 12px;
                                    font-weight: 600;
                                    display: inline-flex;
                                    align-items: center;
                                    gap: 10px;
                                    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
                                    transition: transform 0.2s;
                                " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                                    🚀 Server Download (Instant)
                                </a>
                            </div>
                        """, unsafe_allow_html=True)

                        # Standard Fallback Download (Works on Mac)
                        with open(out, "rb") as f:
                            st.download_button(
                                "📥  Download to Mac (Standard)",
                                data=f,
                                file_name=output_filename,
                                mime="video/mp4"
                            )
                except Exception as e:
                    st.error(f"Render failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)  # close .video-tool

if __name__ == "__main__":
    main()
