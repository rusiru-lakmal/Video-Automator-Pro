import os
from moviepy import VideoFileClip, vfx
import numpy as np
import cv2

def enhance_frame(frame, vivid_mode=False):
    """
    Applies high-detail sharpening and optionally a vivid color boost.
    """
    # 1. Detail & Clarity Boost (Laplacian Sharpening)
    # This brings out fine details without creating too much noise
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(frame, -1, kernel)
    
    # Blend sharpened with original to control intensity
    enhanced = cv2.addWeighted(frame, 0.7, sharpened, 0.3, 0)
    
    # 2. Color Enhancement
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_RGB2HSV)
    if vivid_mode:
        # Aggressive but smooth saturation boost for Vivid Mode
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.4, 0, 255).astype(np.uint8)
        # Slight contrast boost in Value channel
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255).astype(np.uint8)
    else:
        # Standard natural boost
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255).astype(np.uint8)
    
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

def process_video(input_path, output_path, speed=1.05, zoom=1.1, mirror=True, color_jitter=True, enhance_quality=False, vivid_mode=False):
    """
    Processes a video with various effects to avoid copyright detection.
    Compatible with MoviePy 2.x API.
    """
    # Load video
    clip = VideoFileClip(input_path)
    
    # 1. Mirror Effect
    if mirror:
        clip = clip.with_effects([vfx.MirrorX()])
    
    # 2. Speed Control
    if speed != 1.0:
        clip = clip.with_speed_scaled(speed)
        # Note: speed_scaled also shifts audio pitch naturally.
    
    # 3. Zoom & Crop
    if zoom > 1.0:
        w, h = clip.size
        # Calculate the size of the crop area
        new_w, new_h = w / zoom, h / zoom
        # Crop center
        clip = clip.cropped(
            x_center=w/2, y_center=h/2, 
            width=new_w, height=new_h
        )
        
        # Ensure target dimensions are even for H.264 encoder
        target_w = int(w // 2) * 2
        target_h = int(h // 2) * 2
        
        # Resize back to even original dimensions
        clip = clip.resized(width=target_w, height=target_h)
    else:
        # Even if no zoom, ensure original dimensions are even
        w, h = clip.size
        if w % 2 != 0 or h % 2 != 0:
            target_w = (w // 2) * 2
            target_h = (h // 2) * 2
            clip = clip.resized(width=target_w, height=target_h)
        
    # 4. Color Jitter (Subtle brightness/contrast)
    if color_jitter:
        # Subtle increase in contrast and slight brightness shift
        clip = clip.with_effects([vfx.LumContrast(lum=5, contrast=0.05)])
    
    # 5. Quality Enhancement (Sharpening & Saturation)
    if enhance_quality:
        clip = clip.image_transform(lambda f: enhance_frame(f, vivid_mode=vivid_mode))
    
    # Final safety check: Force even dimensions using NATIVE cropping (Much faster)
    final_w, final_h = clip.size
    if final_w % 2 != 0 or final_h % 2 != 0:
        safe_w = (final_w // 2) * 2
        safe_h = (final_h // 2) * 2
        clip = clip.cropped(x1=0, y1=0, x2=safe_w, y2=safe_h)

    ffmpeg_params = [
        "-crf", "23", # Slightly higher CRF for speed (23 is standard)
        "-pix_fmt", "yuv420p"
    ]
    
    clip.write_videofile(output_path, 
                        codec='libx264', 
                        audio_codec='aac',
                        audio_bitrate='320k', 
                        temp_audiofile='temp-audio.m4a', 
                        remove_temp=True,
                        threads=os.cpu_count(), 
                        fps=clip.fps,
                        preset='medium', # Balanced speed and quality
                        ffmpeg_params=ffmpeg_params) 
    
    clip.close()
    return output_path
