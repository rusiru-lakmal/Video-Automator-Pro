import os
from moviepy import VideoFileClip, vfx
import numpy as np
import cv2

def enhance_frame(frame, vivid_mode=False):
    """
    Advanced detail enhancement using Unsharp Masking and CLAHE.
    """
    # 1. Contrast Limited Adaptive Histogram Equalization (CLAHE)
    # This brings out micro-details in shadows and highlights
    lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # 2. Unsharp Masking (Better than Laplacian for clarity)
    # blurred = cv2.GaussianBlur(enhanced, (5,5), 0)
    # sharpened = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)
    
    # Alternative: Multi-scale sharpening for extreme detail
    gaussian_3 = cv2.GaussianBlur(enhanced, (0, 0), 3)
    sharpened = cv2.addWeighted(enhanced, 1.5, gaussian_3, -0.5, 0)
    
    # 3. Color Enhancement
    hsv = cv2.cvtColor(sharpened, cv2.COLOR_RGB2HSV)
    if vivid_mode:
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.35, 0, 255).astype(np.uint8)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.05, 0, 255).astype(np.uint8)
    else:
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255).astype(np.uint8)
    
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

def remove_watermark_frame(frame):
    """
    Surgically removes the "Veo" watermark from the bottom-right corner.
    Improved version with wider ROI and relaxed thresholds for better coverage.
    """
    h, w = frame.shape[:2]
    
    # 1. Define a wider search region (Bottom-Right)
    # Increased margin to ensure we catch text even if slightly offset
    y_start, y_end = int(h * 0.78), int(h * 0.99)
    x_start, x_end = int(w * 0.72), int(w * 0.99)
    
    # Extract the region of interest (ROI)
    roi = frame[y_start:y_end, x_start:x_end]
    
    # 2. Isolate the watermark text using relaxed color thresholding
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    
    # Threshold for "whitish" pixels - RELAXED to catch semi-transparent parts
    # Lower bound: 100 brightness (was 160)
    # Upper bound saturation: 100 (was 60)
    lower_white = np.array([0, 0, 100]) 
    upper_white = np.array([180, 100, 255])
    
    mask_roi = cv2.inRange(hsv_roi, lower_white, upper_white)
    
    # 3. Refine the mask - STRONGER DILATION
    # Larger kernel and more iterations ensure anti-aliased edges are covered
    kernel = np.ones((5, 5), np.uint8)
    mask_roi = cv2.dilate(mask_roi, kernel, iterations=2)
    
    # 4. Create the full-frame mask
    full_mask = np.zeros((h, w), dtype=np.uint8)
    full_mask[y_start:y_end, x_start:x_end] = mask_roi
    
    # 5. Apply Inpainting
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    inpainted_bgr = cv2.inpaint(frame_bgr, full_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    
    return cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)

def process_video(input_path, output_path, speed=1.05, zoom=1.1, mirror=True, color_jitter=True, 
                  enhance_quality=False, vivid_mode=False, cinematic_mode=False, 
                  remove_veo_watermark=False, upscale_4k=False):
    """
    Processes a video with advanced enhancements, optional 4K upscaling, and watermark removal.
    """
    clip = VideoFileClip(input_path)
    
    # 1. Handle Upscaling / Cinematic Reframing
    if cinematic_mode:
        target_ratio = 1080 / 1920
        w, h = clip.size
        current_ratio = w / h
        if current_ratio > target_ratio:
            new_w = h * target_ratio
            clip = clip.cropped(x_center=w/2, y_center=h/2, width=new_w, height=h)
        else:
            new_h = w / target_ratio
            clip = clip.cropped(x_center=w/2, y_center=h/2, width=w, height=new_h)
        
        # If upscale_4k is on, we'll hit 2160x3840 (vertical 4K)
        target_w, target_h = (2160, 3840) if upscale_4k else (1080, 1920)
        clip = clip.resized(width=target_w, height=target_h)
    elif upscale_4k:
        # Standard 4K (3840x2160)
        clip = clip.resized(width=3840, height=2160)
    
    # 2. Mirror Effect
    if mirror:
        clip = clip.with_effects([vfx.MirrorX()])
    
    # 3. Speed Control
    if speed != 1.0:
        clip = clip.with_speed_scaled(speed)
    
    # 4. Zoom & Crop
    if zoom > 1.0:
        w, h = clip.size
        new_w, new_h = w / zoom, h / zoom
        clip = clip.cropped(x_center=w/2, y_center=h/2, width=new_w, height=new_h)
        
        # Resize back to current dimensions (ensuring even)
        target_w, target_h = (int(w // 2) * 2), (int(h // 2) * 2)
        clip = clip.resized(width=target_w, height=target_h)
        
    # 5. Color Jitter
    if color_jitter:
        clip = clip.with_effects([vfx.LumContrast(lum=5, contrast=0.05)])
    
    # 6. Cinematic Grading
    if cinematic_mode:
        clip = clip.with_effects([
            vfx.GammaCorrection(gamma=1.2),
            vfx.LumContrast(lum=0, contrast=0.1),
            vfx.MultiplyColor(1.05)
        ])
    
    # 7. Watermark Removal (Surgical)
    if remove_veo_watermark:
        clip = clip.image_transform(remove_watermark_frame)

    # 8. Detail Enhancement (Pro Sharpening & CLAHE)
    if enhance_quality:
        clip = clip.image_transform(lambda f: enhance_frame(f, vivid_mode=vivid_mode or cinematic_mode))
    
    # Final safety check: Force even dimensions
    final_w, final_h = clip.size
    if final_w % 2 != 0 or final_h % 2 != 0:
        safe_w = (final_w // 2) * 2
        safe_h = (final_h // 2) * 2
        clip = clip.cropped(x1=0, y1=0, x2=safe_w, y2=safe_h)

    # High-fidelity encoding parameters
    ffmpeg_params = [
        "-crf", "17", # Visually lossless (lower is better quality)
        "-pix_fmt", "yuv420p",
        "-color_range", "1" # Ensure full color range
    ]
    
    render_preset = 'slow' if (cinematic_mode or upscale_4k) else 'medium'
    
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
