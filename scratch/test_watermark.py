import numpy as np
import cv2
import os
from video_processor import remove_watermark_frame

def test_watermark_removal():
    # Create a dummy frame (black)
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Add a white "watermark" in the bottom right
    # Region used in code: x1, y1 = int(w * 0.82), int(h * 0.88), x2, y2 = int(w * 0.98), int(h * 0.97)
    w, h = 1920, 1080
    x1, y1 = int(w * 0.85), int(h * 0.90)
    x2, y2 = int(w * 0.95), int(h * 0.95)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), -1)
    
    # Save original frame for comparison
    cv2.imwrite("test_original.png", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    # Process the frame
    processed_frame = remove_watermark_frame(frame)
    
    # Save processed frame
    cv2.imwrite("test_processed.png", cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
    
    print("Test frames saved to test_original.png and test_processed.png")
    
    # Check if the area is no longer pure white
    # (Inpainting on black with a white box might result in some artifacts, but it shouldn't be the original box)
    original_box_sum = np.sum(frame[y1:y2, x1:x2])
    processed_box_sum = np.sum(processed_frame[y1:y2, x1:x2])
    
    if processed_box_sum < original_box_sum:
        print("Success: The watermark area was modified.")
    else:
        print("Failure: The watermark area remains unchanged.")

if __name__ == "__main__":
    test_watermark_removal()
