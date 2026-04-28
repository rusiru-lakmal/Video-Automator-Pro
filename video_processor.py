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

def remove_watermark_frame(frame):
    """
    Surgically removes the "Veo" watermark from the bottom-right corner.
    Uses thresholding to isolate only the text pixels, minimizing blur.
    """
    h, w = frame.shape[:2]
    
    # 1. Define the search region (Bottom-Right)
    # We use a slightly larger area to ensure we capture the whole "veo" text
    y_start, y_end = int(h * 0.85), int(h * 0.98)
    x_start, x_end = int(w * 0.80), int(w * 0.99)
    
    # Extract the region of interest (ROI)
    roi = frame[y_start:y_end, x_start:x_end]
    
    # 2. Isolate the watermark text using color thresholding
    # Veo watermark is usually semi-transparent white/grey.
    # We look for high brightness (Value channel in HSV) and low saturation.
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    
    # Threshold for "whitish" pixels
    # Lower bound: moderate brightness, low saturation
    # Upper bound: max brightness, low-moderate saturation (to catch greyish edges)
    lower_white = np.array([0, 0, 160]) # High value (brightness)
    upper_white = np.array([180, 60, 255]) # Low saturation
    
    mask_roi = cv2.inRange(hsv_roi, lower_white, upper_white)
    
    # 3. Refine the mask
    # Apply morphological dilation to ensure the edges of the text are fully covered
    kernel = np.ones((3, 3), np.uint8)
    mask_roi = cv2.dilate(mask_roi, kernel, iterations=1)
    
    # 4. Create the full-frame mask
    full_mask = np.zeros((h, w), dtype=np.uint8)
    full_mask[y_start:y_end, x_start:x_end] = mask_roi
    
    # 5. Apply Inpainting
    # Use a small radius for surgical precision
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    inpainted_bgr = cv2.inpaint(frame_bgr, full_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    return cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)

def process_video(input_path, output_path, speed=1.05, zoom=1.1, mirror=True, color_jitter=True, 
                  enhance_quality=False, vivid_mode=False, cinematic_mode=False, remove_veo_watermark=False):
    """
    Processes a video with various effects to avoid copyright detection and add cinematic quality.
    """
    # Load video
    clip = VideoFileClip(input_path)
    
    # 1. Cinematic Framing (Crop to Fill 1080x1920)
    if cinematic_mode:
        target_ratio = 1080 / 1920
        w, h = clip.size
        current_ratio = w / h
        
        if current_ratio > target_ratio:
            # Video is too wide, crop sides
            new_w = h * target_ratio
            clip = clip.cropped(x_center=w/2, y_center=h/2, width=new_w, height=h)
        else:
            # Video is too tall, crop top/bottom
            new_h = w / target_ratio
            clip = clip.cropped(x_center=w/2, y_center=h/2, width=w, height=new_h)
        
        # Resize to standard Reels resolution
        clip = clip.resized(width=1080, height=1920)
    
    # 2. Mirror Effect
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
    
    # 5. Cinematic Effects
    if cinematic_mode:
        # Gamma correction, Contrast boost, and Brightness multiplication
        clip = clip.with_effects([
            vfx.GammaCorrection(gamma=1.2),
            vfx.LumContrast(lum=0, contrast=0.1), # +10% Contrast
            vfx.MultiplyColor(1.05) # Subtle brightness boost
        ])
    
    # 6. Watermark Removal
    if remove_veo_watermark:
        clip = clip.image_transform(remove_watermark_frame)

    # 7. Quality Enhancement (Sharpening & Saturation)
    if enhance_quality:
        clip = clip.image_transform(lambda f: enhance_frame(f, vivid_mode=vivid_mode or cinematic_mode))
    
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
    
    # Final rendering with High-Quality Settings
    # Use 'slow' for Cinematic Mode for best detail retention
    render_preset = 'slow' if cinematic_mode else 'medium'
    
    clip.write_videofile(output_path, 
                        codec='libx264', 
                        audio_codec='aac',
                        audio_bitrate='320k', 
                        temp_audiofile='temp-audio.m4a', 
                        remove_temp=True,
                        threads=os.cpu_count(), 
                        fps=clip.fps,
                        preset=render_preset,
                        ffmpeg_params=ffmpeg_params) 
    
    clip.close()
    return output_path
