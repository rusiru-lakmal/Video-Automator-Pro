import numpy as np
import cv2
from video_processor import enhance_frame

def test_4k_enhancement():
    # Create a small low-res frame (e.g., 360p)
    low_res = np.full((360, 640, 3), (100, 100, 100), dtype=np.uint8)
    cv2.putText(low_res, "Test Detail", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # 1. Test Upscaling (Manual check of logic)
    # Standard 4K is 3840x2160
    high_res = cv2.resize(low_res, (3840, 2160), interpolation=cv2.INTER_LANCZOS4)
    print(f"Upscaled resolution: {high_res.shape[1]}x{high_res.shape[0]}")
    
    if high_res.shape == (2160, 3840, 3):
        print("Success: Resolution is 4K (3840x2160).")
    else:
        print("Failure: Incorrect resolution.")
        
    # 2. Test Enhancement
    enhanced = enhance_frame(high_res)
    cv2.imwrite("test_4k_enhanced.png", cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR))
    print("Enhanced 4K sample saved to test_4k_enhanced.png")
    
    # Check if CLAHE/Sharpening changed the image
    if not np.array_equal(high_res, enhanced):
        print("Success: Enhancement logic modified the pixels.")
    else:
        print("Failure: Enhancement logic had no effect.")

if __name__ == "__main__":
    test_4k_enhancement()
