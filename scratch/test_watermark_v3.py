import numpy as np
import cv2
import os
from video_processor import remove_watermark_frame

def test_watermark_removal_v3():
    # Create a dummy frame (complex texture/gradient)
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    for i in range(1080):
        frame[i, :, :] = [20 + i//20, 30 + i//30, 50] # Gradient background
    
    # Add a SEMI-TRANSPARENT "veo" watermark in the bottom right
    # Brightness around 130 (which was missed by the previous 160 threshold)
    w, h = 1920, 1080
    y_start, x_start = int(h * 0.90), int(w * 0.85)
    
    # Create a separate layer for text and blend it
    text_layer = frame.copy()
    cv2.putText(text_layer, "veo", (x_start, y_start), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 200), 2, cv2.LINE_AA)
    
    # Blend with 50% opacity
    cv2.addWeighted(text_layer, 0.5, frame, 0.5, 0, frame)
    
    # Save original frame for comparison
    cv2.imwrite("test_original_v3.png", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    # Process the frame
    processed_frame = remove_watermark_frame(frame)
    
    # Save processed frame
    cv2.imwrite("test_processed_v3.png", cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
    
    # Create the mask as the code would to see if it targets correctly
    roi = frame[int(h * 0.78):int(h * 0.99), int(w * 0.72):int(w * 0.99)]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    lower_white = np.array([0, 0, 100])
    upper_white = np.array([180, 100, 255])
    mask_roi = cv2.inRange(hsv_roi, lower_white, upper_white)
    cv2.imwrite("test_mask_v3.png", mask_roi)
    
    print("Test frames saved: test_original_v3.png, test_processed_v3.png, test_mask_v3.png")
    
    # Check if the text area is cleared
    text_area_orig = frame[y_start-30:y_start+10, x_start:x_start+80]
    text_area_proc = processed_frame[y_start-30:y_start+10, x_start:x_start+80]
    
    if np.mean(text_area_proc) < np.mean(text_area_orig):
        print("Success: The semi-transparent watermark was detected and processed.")
    else:
        print("Failure: The watermark remains.")

if __name__ == "__main__":
    test_watermark_removal_v3()
