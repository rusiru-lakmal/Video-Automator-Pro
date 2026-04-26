import streamlit as st

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Video & Image Automator Pro",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ── Master CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #080810 !important;
    color: #e8e8f0 !important;
    overflow-x: hidden;
}

/* ── Animated Mesh Background ── */
.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(120, 40, 200, 0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(255, 60, 100, 0.10) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(30, 140, 255, 0.10) 0%, transparent 50%);
    animation: meshDrift 18s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes meshDrift {
    0%   { transform: translate(0, 0) rotate(0deg); }
    33%  { transform: translate(2%, 3%) rotate(1deg); }
    66%  { transform: translate(-2%, 1%) rotate(-1deg); }
    100% { transform: translate(1%, -2%) rotate(0.5deg); }
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(12, 12, 20, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(20px) !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* ── App Logo Area ── */
.app-brand {
    padding: 28px 24px 20px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 12px;
}

.app-brand-logo {
    font-size: 1.8rem;
    margin-bottom: 4px;
}

.app-brand-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.3px;
}

.app-brand-tagline {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 2px;
}

/* ── Nav Menu ── */
.nav-section-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: rgba(255,255,255,0.25);
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 16px 24px 8px 24px;
}

/* ── Sidebar Radio Overrides ── */
div[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 11px 20px !important;
    margin: 3px 12px !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.55) !important;
    border: 1px solid transparent !important;
}

div[data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.9) !important;
}

div[data-testid="stRadio"] [aria-checked="true"] ~ label,
div[data-testid="stRadio"] label:has(input:checked) {
    background: rgba(255,255,255,0.07) !important;
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.1) !important;
}

div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
    display: none !important;
}

div[data-testid="stRadio"] > div {
    gap: 0 !important;
}

/* Hide radio bullets */
div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}

/* ── Sidebar Status Badge ── */
.status-card {
    margin: 16px 16px 0 16px;
    padding: 14px 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
}

.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 7px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.8); }
}

.status-text {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.5);
    line-height: 1.6;
}

/* ── Main Content Area ── */
.block-container {
    padding: 2rem 3rem 6rem 3rem !important;
    max-width: 1400px !important;
    position: relative;
    z-index: 1;
}

/* ── Page Hero Banner ── */
.hero-banner {
    position: relative;
    overflow: hidden;
    border-radius: 20px;
    padding: 48px 56px;
    margin-bottom: 40px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
}

.hero-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,60,100,0.08) 0%, transparent 60%);
    pointer-events: none;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    background: rgba(255,60,100,0.12);
    border: 1px solid rgba(255,60,100,0.25);
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #ff6b8a;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 3.6rem;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -2px;
    color: #ffffff;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #ffffff 30%, rgba(255,60,100,0.9) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-title-image {
    background: linear-gradient(135deg, #ffffff 30%, rgba(30,140,255,0.9) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1.05rem;
    font-weight: 400;
    color: rgba(255,255,255,0.45);
    max-width: 540px;
    line-height: 1.6;
}

/* ── Stats Row ── */
.stats-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 36px;
}

.stat-pill {
    padding: 8px 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 100px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.5);
    font-weight: 500;
}

.stat-pill span {
    color: #ffffff;
    font-weight: 700;
}

/* ── Section Headers ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.3);
    margin-bottom: 16px;
}

/* ── Glass Cards ── */
.glass-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px;
    transition: border-color 0.3s ease, background 0.3s ease;
    margin-bottom: 16px;
}

.glass-card:hover {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.12);
}

/* ── Card Headers ── */
.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}

.card-icon {
    width: 36px;
    height: 36px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.icon-red  { background: rgba(255,60,100,0.15); }
.icon-blue { background: rgba(30,140,255,0.15); }
.icon-gold { background: rgba(255,180,50,0.15); }

.card-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #ffffff;
}

.card-subtitle {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.35);
    margin-top: 1px;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 2px dashed rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    transition: 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(255,60,100,0.35) !important;
    background: rgba(255,60,100,0.03) !important;
}

[data-testid="stFileUploader"] section {
    background: transparent !important;
    border: none !important;
    padding: 28px !important;
}

[data-testid="stFileUploader"] section > input + div {
    background: transparent !important;
    border: none !important;
}

[data-testid="stFileUploader"] section small {
    color: rgba(255,255,255,0.3) !important;
}

[data-testid="stFileUploadDropzone"] {
    background: transparent !important;
    border: none !important;
}

/* ── Uploader Browse Button ── */
[data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.8) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 7px 16px !important;
    width: auto !important;
    transition: all 0.2s ease !important;
}

[data-testid="stFileUploader"] button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* ── Sliders ── */
.stSlider [data-testid="stWidgetLabel"] p {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* Slider track */
.stSlider [data-testid="stSlider"] > div > div > div {
    background: rgba(255,255,255,0.08) !important;
}

/* Slider value label */
.stSlider [data-testid="stSlider"] p {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

/* ── Checkboxes ── */
.stCheckbox label p {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.65) !important;
}

.stCheckbox {
    padding: 4px 0 !important;
}

/* ── Primary Buttons ── */
.stButton > button {
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px !important;
    padding: 14px 28px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    width: 100% !important;
}

/* Video Tool Button */
.video-tool .stButton > button {
    background: linear-gradient(135deg, #ff3c64 0%, #c8103e 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(255,60,100,0.25) !important;
}

.video-tool .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(255,60,100,0.45) !important;
}

/* Image Tool Button */
.image-tool .stButton > button {
    background: linear-gradient(135deg, #1e8cff 0%, #0057cc 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(30,140,255,0.25) !important;
}

.image-tool .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(30,140,255,0.45) !important;
}

/* ── Download Button ── */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,255,255,0.11) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* ── Alerts & Info ── */
.stAlert {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    border-left: 3px solid rgba(255,255,255,0.2) !important;
}

/* ── Dividers ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Video Player ── */
video {
    border-radius: 12px !important;
    width: 100% !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* Spinner */
.stSpinner > div {
    border-top-color: #ff3c64 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Import modules ────────────────────────────────────────────────────────────
import app as video_module
import image_app as image_module

# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class="app-brand">
            <div class="app-brand-logo">⚡</div>
            <div class="app-brand-name">Automator Pro</div>
            <div class="app-brand-tagline">AI Content Suite</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="nav-section-label">Suite</div>', unsafe_allow_html=True)

        mode = st.radio(
            "nav",
            ["🎬  Video Automator", "✨  Image Architect"],
            label_visibility="collapsed",
            key="nav_radio"
        )

        st.markdown("""
        <div class="status-card">
            <div class="status-text">
                <span class="status-dot"></span><strong style="color:#fff">All Systems Online</strong><br>
                <span style="margin-left:14px">Apple Silicon · MPS Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return mode

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    mode = render_sidebar()

    if "Video" in mode:
        video_module.main()
    else:
        image_module.main()

if __name__ == "__main__":
    main()
