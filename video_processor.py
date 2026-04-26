import os
from moviepy import VideoFileClip, vfx
import numpy as np
import cv2

def enhance_frame(frame):
    """
    Applies high-quality sharpening, bilateral denoising, and color enhancement.
    """
    # 1. Bilateral Denoising (Removes noise while preserving edges)
    # d=5 (pixel neighborhood), sigmaColor=75, sigmaSpace=75
    denoised = cv2.bilateralFilter(frame, 5, 75, 75)
    
    # 2. Sharpening (Unsharp Mask)
    gaussian_blur = cv2.GaussianBlur(denoised, (0, 0), 3)
    sharpened = cv2.addWeighted(denoised, 1.5, gaussian_blur, -0.5, 0)
    
    # 3. Color Enhancement (Vibrance boost)
    hsv = cv2.cvtColor(sharpened, cv2.COLOR_RGB2HSV)
    # Smoothly increase saturation
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255).astype(np.uint8)
    enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    return enhanced

def process_video(input_path, output_path, speed=1.05, zoom=1.1, mirror=True, color_jitter=True, enhance_quality=False):
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
        clip = clip.image_transform(enhance_frame)
    
    # Final safety check: Force even dimensions at the raw pixel level
    # This is the 'Nuclear Option' to ensure FFMPEG never sees an odd dimension.
    def force_even_dimensions(frame):
        h, w = frame.shape[:2]
        new_h = (h // 2) * 2
        new_w = (w // 2) * 2
        if h != new_h or w != new_w:
            return frame[:new_h, :new_w]
        return frame

    clip = clip.image_transform(force_even_dimensions)

    ffmpeg_params = [
        "-crf", "18",
        "-pix_fmt", "yuv420p" # Ensure compatibility with all players
    ]
    
    clip.write_videofile(output_path, 
                        codec='libx264', 
                        audio_codec='aac',
                        audio_bitrate='320k', # Studio Quality Audio
                        temp_audiofile='temp-audio.m4a', 
                        remove_temp=True,
                        threads=os.cpu_count(), # Use all available cores
                        fps=clip.fps,
                        preset='slow',
                        ffmpeg_params=ffmpeg_params,
                        logger=None) # Hide logs for cleaner output
    
    clip.close()
    return output_path
