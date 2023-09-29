# There are two threads, one is responsible to view the frames from the RTSP feed
# The second is responsible for dequeuing the data frames and saving it into the data folder

import cv2
import time
import logging
import numpy as np
import os
import queue 
import threading

def FrameCorrupt(Frame):
    AveragePixelValue = np.mean(Frame)
    CorruptThreshold = 10
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
            
            FrameQueue = queue.Queue()

            def SaveFrames():
                if not os.path.exists("test"):
                    os.makedirs("test")

                FrameCount = 0
                while True:
                    try:
                        frame = FrameQueue.get()
                        if frame is not None:
                            FrameCount += 1
                            # Saving the Frames
                            FileName = os.path.join("test", f"frame_{FrameCount}.jpg")
                            cv2.imwrite(FileName, frame)
                    except Exception as e:
                        logging.exception(e)

            # Start the Frame Saving thread
            SaveThread = threading.Thread(target=SaveFrames)
            SaveThread.daemon = True
            SaveThread.start()
            
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
                        
                FrameQueue.put(Frame)

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
