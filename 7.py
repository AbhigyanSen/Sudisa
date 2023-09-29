import cv2
import time
import logging
import numpy as np
import os
import queue 
import threading

def FrameCorrupt(Frame):
    # Calculate the average pixel value of the Frame
    AveragePixelValue = np.mean(Frame)

    # Define a threshold below which the Frame is considered corrupt
    # Adjust this threshold as needed for your specific use case
    CorruptThreshold = 10

    # Check if the average pixel value is below the threshold
    return AveragePixelValue < CorruptThreshold

# Establish Connection
def Connection(RtspURL, MaxRetries=3, RetryInterval=10, MaxCorruptFrameDuration=30):  
    for Retry in range(MaxRetries):
        try:
            # Connect to the RTSP stream
            cap = cv2.VideoCapture(RtspURL)
            
            if not cap.isOpened():
                print("Failed to Open RTSP Stream. Retrying in {} seconds (Retry {}/{})".format(RetryInterval, Retry + 1, MaxRetries))
                time.sleep(RetryInterval)
                continue

            CorruptFrameStartTime = None
            
            while True:
                ret, Frame = cap.read()
                
                # Handling Camera Shutdown
                if not ret:
                    print("No video feed available. Retrying in {} seconds (Retry {}/{})".format(RetryInterval, Retry + 1, MaxRetries))
                    break
                
                # Handling Corrupt Frames
                if FrameCorrupt(Frame):
                    if CorruptFrameStartTime is None:
                        CorruptFrameStartTime = time.time()
                    elif (time.time() - CorruptFrameStartTime) >= MaxCorruptFrameDuration:
                        print("Corrupt frames received for over {} seconds. Retry (Retry {}/{})".format(MaxCorruptFrameDuration, Retry + 1, MaxRetries))
                        break
                
                cv2.imshow("Video", Frame)
                k = cv2.waitKey(1)
                if k == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            if ret:
                print("Connection established successfully.")
                break  # Connection successful, exit the Retry loop
            else:
                # Reset the Retry counter if there's a successful connection
                Retry = 0
                time.sleep(RetryInterval)

        except Exception as e:
            logging.exception(e)
            Retry += 1
            time.sleep(RetryInterval)

    if Retry == MaxRetries:
        print("Failed to establish connection after {} Retries.".format(MaxRetries))

# Example Case
RtspURL = "rtsp://admin:Sheraton123@10.111.111.106:554/Streaming/Channels/501/"

Connection(RtspURL)