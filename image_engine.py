import torch
import cv2
import numpy as np
from PIL import Image, ImageFilter
from gfpgan import GFPGANer
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from rembg import remove
import os

class AIImageArchitect:
    def __init__(self):
        # 1. Device Setup (Apple Silicon Optimization)
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("Using Apple Silicon (MPS) acceleration")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            print("Using NVIDIA (CUDA) acceleration")
        else:
            self.device = torch.device("cpu")
            print("Using CPU")

        # 2. Initialize Models (These will download automatically on first run)
        self.face_restorer = self._init_gfpgan()
        self.upscaler = self._init_realesrgan()

    def _init_gfpgan(self):
        model_path = 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth'
        # upscale=2 by default for face restoration step
        restorer = GFPGANer(
            model_path=model_path,
            upscale=2,
            arch='clean',
            channel_multiplier=2,
            device=self.device
        )
        return restorer

    def _init_realesrgan(self):
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
        upscaler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True if self.device.type != 'cpu' else False,
            device=self.device
        )
        return upscaler

    def enhance(self, input_image, intensity=0.5, bokeh=False, brightness=1.0):
        # Convert PIL to CV2 (BGR)
        img = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2BGR)
        
        # Step 1: Face Restoration (GFPGAN)
        _, _, restored_img = self.face_restorer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        
        # Step 2: 4K Upscaling (Real-ESRGAN)
        # We only upscale if needed, but here we force it for 4K quality
        upscaled_img, _ = self.upscaler.enhance(restored_img, outscale=4)
        
        # Step 3: Background Bokeh (rembg)
        if bokeh:
            # Convert back to PIL for rembg
            pil_img = Image.fromarray(cv2.cvtColor(upscaled_img, cv2.COLOR_BGR2RGB))
            # Get foreground mask
            subject = remove(pil_img)
            # Create blurred background
            background = pil_img.filter(ImageFilter.GaussianBlur(radius=15))
            # Composite
            pil_img = Image.alpha_composite(background.convert('RGBA'), subject.convert('RGBA'))
            upscaled_img = cv2.cvtColor(np.array(pil_img.convert('RGB')), cv2.COLOR_RGB2BGR)

        # Step 4: Cinematic Grading
        processed = self._apply_cinematic_grade(upscaled_img, brightness)
        
        # Convert back to RGB for PIL
        return Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))

    def _apply_cinematic_grade(self, img, brightness):
        # Convert to float for processing
        img = img.astype(np.float32) / 255.0
        
        # Gamma Correction (1.2)
        img = np.power(img, 1/1.2)
        
        # Brightness/Contrast
        img = img * brightness
        img = np.clip(img, 0, 1)
        
        # Convert back to uint8
        img = (img * 255).astype(np.uint8)
        
        # Saturation boost (1.1x)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.1, 0, 255).astype(np.uint8)
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Laplacian Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        img = cv2.filter2D(img, -1, kernel)
        
        return img
