import streamlit as st
import os
import tempfile
from video_processor import process_video

# Page configuration
st.set_page_config(
    page_title="Video Automator Pro",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #e94560;
    }
    .stButton>button {
        background-color: #e94560;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0f3460;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    .stSlider > div > div > div > div {
        background-color: #e94560;
    }
    .header-text {
        text-align: center;
        color: #e94560;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-text {
        text-align: center;
        color: #95a5a6;
        margin-bottom: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="header-text">🎬 Video Automator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Bypass copyright detection with advanced AI-powered transformations</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📁 Upload Video")
        uploaded_file = st.file_uploader("Choose an MP4 file", type=['mp4'])
        
        if uploaded_file:
            st.video(uploaded_file)

    with col2:
        st.subheader("⚙️ Transformation Settings")
        
        # Sliders
        speed = st.slider("Playback Speed", 0.5, 2.0, 1.05, 0.01, help="Slightly increasing speed helps bypass fingerprinting.")
        zoom = st.slider("Zoom Level", 1.0, 2.0, 1.10, 0.05, help="Zooming in removes edge patterns used for detection.")
        
        # Checkboxes
        col_check1, col_check2 = st.columns(2)
        with col_check1:
            mirror = st.checkbox("Mirror Effect", value=True, help="Flips the video horizontally.")
        with col_check2:
            color_jitter = st.checkbox("Color Jitter", value=True, help="Subtle brightness/contrast changes.")

        enhance_quality = st.checkbox("✨ AI Quality Enhancement (Beta)", value=False, help="Uses sharpening and color boosting to enhance clarity, similar to basic Remini effects.")

        st.markdown("---")
        
        if st.button("🚀 Process & Render"):
            if uploaded_file is not None:
                try:
                    # Create a temporary directory for processing
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        # Save uploaded file
                        input_path = os.path.join(tmp_dir, "input_video.mp4")
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        output_path = os.path.join(tmp_dir, "processed_video.mp4")
                        
                        with st.spinner("Processing video... This may take a few minutes depending on length."):
                            process_video(
                                input_path, 
                                output_path, 
                                speed=speed, 
                                zoom=zoom, 
                                mirror=mirror, 
                                color_jitter=color_jitter,
                                enhance_quality=enhance_quality
                            )
                        
                        st.success("✅ Video Processed Successfully!")
                        
                        # Provide download button
                        with open(output_path, "rb") as file:
                            btn = st.download_button(
                                label="📥 Download Processed Video",
                                data=file,
                                file_name="automator_result.mp4",
                                mime="video/mp4"
                            )
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please upload a video first!")

if __name__ == "__main__":
    main()
