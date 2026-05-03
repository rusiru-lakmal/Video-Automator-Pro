import os
from moviepy import VideoFileClip, vfx, AudioFileClip
import imageio_ffmpeg
import random
import numpy as np
import cv2
import torch
from PIL import Image
from torchvision.transforms.functional import to_tensor, to_pil_image

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

def comic_effect(frame):
    """
    High-quality Comic/Cartoon transformation using K-Means clustering
    for clean color blocks and adaptive outlines.
    """
    # 1. Color Quantization using K-Means (The "Pro" Look)
    data = frame.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    K = 8  # Number of distinct colors (lower = more "comic" look)
    _, label, center = cv2.kmeans(data, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    quantized = center[label.flatten()].reshape(frame.shape)

    # 2. Smooth the quantized image to remove "pixel jitter"
    color = cv2.medianBlur(quantized, 5)

    # 3. Create strong, clean outlines
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 7), 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 9, 8)

    # 4. Combine and boost vibrancy
    edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    cartoon = cv2.bitwise_and(color, edges_3ch)
    
    return cartoon

def painterly_effect(frame):
    """
    Transforms a frame into a soft, hand-painted illustration style 
    using multi-stage Bilateral Filtering and Saturation curves.
    """
    # 1. Iterative Bilateral Filtering (Creates the "Ghibli" soft look)
    color = frame.copy()
    for _ in range(2):
        color = cv2.bilateralFilter(color, d=9, sigmaColor=75, sigmaSpace=75)

    # 2. Median Blur to flatten large areas
    color = cv2.medianBlur(color, 5)

    # 3. Color Grading (Warmth and Pop)
    hsv = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.3, 0, 255).astype(np.uint8)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255).astype(np.uint8)
    
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

def add_noise(frame, amount=0.03):
    """
    Adds subtle film grain/noise to break pixel-perfect hash matching.
    """
    noise = np.random.normal(0, 255 * amount, frame.shape).astype(np.float32)
    noisy_frame = frame.astype(np.float32) + noise
    return np.clip(noisy_frame, 0, 255).astype(np.uint8)

def shift_audio_pitch(audio_path, output_path, n_semitones=0.5):
    """
    Shifts audio pitch using ffmpeg to bypass audio fingerprinting.
    Uses imageio_ffmpeg to find the ffmpeg binary for reliability.
    """
    factor = 2**(n_semitones/12)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd = (
        f"\"{ffmpeg_bin}\" -y -i \"{audio_path}\" "
        f"-af \"asetrate=44100*{factor},atempo={1/factor}\" "
        f"\"{output_path}\""
    )
    
    # Run command and check for errors
    exit_code = os.system(cmd)
    if exit_code != 0:
        raise RuntimeError(f"FFmpeg pitch shift failed with exit code {exit_code}. Ensure ffmpeg is installed.")
        
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"FFmpeg failed to create pitched audio file: {output_path}")
        
    return output_path

def draw_text_overlay(frame, text, position="top"):
    """
    Draws a viral headline/hook on the frame using OpenCV.
    """
    if not text:
        return frame
        
    h, w = frame.shape[:2]
    # Font settings
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = w / 800  # Dynamic scale based on width
    thickness = max(2, int(3 * font_scale))
    
    # Get text size
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (w - text_size[0]) // 2
    
    # Background bar
    bar_height = int(text_size[1] * 2.5)
    overlay = frame.copy()
    
    if position == "top":
        text_y = int(bar_height * 0.7)
        cv2.rectangle(overlay, (0, 0), (w, bar_height), (0, 0, 0), -1)
    else:
        text_y = h - int(bar_height * 0.3)
        cv2.rectangle(overlay, (0, h - bar_height), (w, h), (0, 0, 0), -1)
    
    # Blend background
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Draw text with shadow/outline
    cv2.putText(frame, text, (text_x + 2, text_y + 2), font, font_scale, (0, 0, 0), thickness + 1)
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
    
    return frame

def load_ai_model():
    """
    Loads the AnimeGANv2 model from a local weights file.
    """
    # Load the architecture from the hub repo (code only)
    model = torch.hub.load("AK391/animegan2-pytorch:main", "generator", pretrained=False)
    
    # Load the local weights we just downloaded
    weights_path = "face_paint_512_v2.pt"
    if os.path.exists(weights_path):
        state_dict = torch.load(weights_path, map_location="cpu")
        model.load_state_dict(state_dict)
    
    model.eval()
    return model

def apply_ai_style(frame, model, device="cpu"):
    """
    Applies AnimeGANv2 stylization with strict memory optimization.
    Processes at a fixed resolution and upscales back to prevent crashes.
    """
    import gc
    with torch.no_grad():
        # 1. Convert to PIL
        img = Image.fromarray(frame).convert("RGB")
        orig_size = img.size
        
        # 2. STABILITY FIX: Resize to a fixed "AI Friendly" resolution
        # This prevents the server from running out of RAM
        ai_res = 512 
        img = img.resize((ai_res, ai_res), Image.LANCZOS)
        
        input_tensor = to_tensor(img).unsqueeze(0) * 2 - 1
        
        # 3. Run AI Inference
        out = model(input_tensor.to(device)).squeeze(0).cpu()
        
        # 4. Cleanup memory immediately
        del input_tensor
        gc.collect()
        
        # 5. Post-process
        out = (out * 0.5 + 0.5).clamp(0, 1)
        out_img = to_pil_image(out)
        
        # 6. Resize back to original high-quality resolution
        if out_img.size != orig_size:
            out_img = out_img.resize(orig_size, Image.LANCZOS)
            
        return np.array(out_img)


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
                  remove_veo_watermark=False, upscale_4k=False, comic_style=False,
                  painterly_style=False, ai_style=False, 
                  pitch_shift=0.0, add_grain=False, clean_meta=True,
                  viral_hook="", hook_pos="top",
                  progress_callback=None):



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
    
    # 9. Comic Style Effect
    if comic_style:
        clip = clip.image_transform(comic_effect)
    
    # 10. AI / Real Comic Style Effect
    if ai_style:
        model = load_ai_model()
        total_frames = int(clip.duration * clip.fps)
        current_frame = 0
        
        def ai_wrapper(f):
            nonlocal current_frame
            current_frame += 1
            if progress_callback:
                # Use min(1.0, ...) to prevent math errors from exceeding 100%
                progress_callback(min(1.0, current_frame / total_frames))
            return apply_ai_style(f, model)
            
        clip = clip.image_transform(ai_wrapper)
    
    # 11. Painterly/Illustrated Effect (Manual version)
    if painterly_style and not ai_style:
        clip = clip.image_transform(painterly_effect)
    
    # 12. Viral Optimization: Film Grain
    if add_grain:
        clip = clip.image_transform(lambda f: add_noise(f, amount=0.04))

    # 13. Viral Optimization: Audio Pitch Shift
    if pitch_shift != 0.0:
        temp_audio = "temp_orig_audio.wav"
        temp_pitched = "temp_pitched_audio.wav"
        clip.audio.write_audiofile(temp_audio, codec='pcm_s16le')
        shift_audio_pitch(temp_audio, temp_pitched, n_semitones=pitch_shift)
        new_audio = AudioFileClip(temp_pitched)
        clip = clip.with_audio(new_audio)
    
    # 14. Viral Optimization: Hook Overlay
    if viral_hook:
        clip = clip.image_transform(lambda f: draw_text_overlay(f, viral_hook, position=hook_pos))
    
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
    
    if clean_meta:
        ffmpeg_params.extend(["-map_metadata", "-1"]) # Strip all metadata
    
    render_preset = 'slow' if (cinematic_mode or upscale_4k) else 'medium'
    
    clip.write_videofile(output_path, 
                        codec='libx264', 
                        audio_codec='aac',
                        audio_bitrate='320k', 
                        temp_audiofile='temp-audio.m4a', 
                        remove_temp=True,
                        threads=1, # Crucial for 2GB RAM servers to prevent OOM
                        fps=clip.fps,
                        preset=render_preset,
                        ffmpeg_params=ffmpeg_params) 
    
    # Cleanup pitched audio temps
    if pitch_shift != 0.0:
        if os.path.exists("temp_orig_audio.wav"): os.remove("temp_orig_audio.wav")
        if os.path.exists("temp_pitched_audio.wav"): os.remove("temp_pitched_audio.wav")

    clip.close()
    return output_path
