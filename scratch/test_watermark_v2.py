import numpy as np
import cv2
import os
from video_processor import remove_watermark_frame

def test_watermark_removal():
    # Create a dummy frame (dark blue background with some noise)
    frame = np.full((1080, 1920, 3), (20, 20, 40), dtype=np.uint8)
    
    # Add a white "veo" watermark in the bottom right
    w, h = 1920, 1080
    y_start, x_start = int(h * 0.90), int(w * 0.85)
    
    # Simulate text with white color
    cv2.putText(frame, "veo", (x_start, y_start), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Save original frame for comparison
    cv2.imwrite("test_original_v2.png", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    # Process the frame
    processed_frame = remove_watermark_frame(frame)
    
    # Save processed frame
    cv2.imwrite("test_processed_v2.png", cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
    
    # Create the mask as the code would to see if it targets correctly
    roi = frame[int(h * 0.85):int(h * 0.98), int(w * 0.80):int(w * 0.99)]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([180, 60, 255])
    mask_roi = cv2.inRange(hsv_roi, lower_white, upper_white)
    cv2.imwrite("test_mask_v2.png", mask_roi)
    
    print("Test frames saved: test_original_v2.png, test_processed_v2.png, test_mask_v2.png")
    
    # Check if the text is gone
    # If the mask was effective, the white pixels should be gone
    text_area = frame[y_start-30:y_start+10, x_start:x_start+80]
    processed_text_area = processed_frame[y_start-30:y_start+10, x_start:x_start+80]
    
    if np.mean(processed_text_area) < np.mean(text_area):
        print("Success: The watermark text was significantly reduced/removed.")
    else:
        print("Failure: The watermark text remains.")

if __name__ == "__main__":
    test_watermark_removal()
