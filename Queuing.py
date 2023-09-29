# There are two threads, one is responsible to view the frames from the RTSP feed
# The second is responsible for dequeuing the data frames and saving it into the data folder

import cv2
import time
import logging
import os
import queue 
import threading

# Establish Connection
def Connection(RtspURL, MaxRetries=3, RetryInterval=10, MaxCorruptFrameDuration=30):
    Retries = 0
    CorruptFrameStartTime = None

    # Create a queue to hold frames
    FrameQueue = queue.Queue()

    def SaveFrames():
        # Create the "data" folder if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

        FrameCount = 0
        while True:
            try:
                frame = FrameQueue.get()
                if frame is not None:
                    FrameCount += 1
                    # Save the frame as an image in the "data" folder
                    filename = os.path.join("data", f"frame_{FrameCount}.jpg")
                    cv2.imwrite(filename, frame)
            except Exception as e:
                logging.exception(e)

    # Start the frame saving thread
    SaveThread = threading.Thread(target=SaveFrames)
    SaveThread.daemon = True
    SaveThread.start()

    while Retries < MaxRetries:
        try:
            # Connect to the RTSP stream
            Video = cv2.VideoCapture(RtspURL)

            if not Video.isOpened():
                print("Failed to Open RTSP Stream. Retrying in {} seconds.".format(RetryInterval))
                time.sleep(RetryInterval)
                continue

            while True:
                _, Frame = Video.read()

                # Handling Camera Shutdown
                if _ is False:
                    print("No video feed available. Retrying in {} seconds.".format(RetryInterval))
                    time.sleep(RetryInterval)
                    continue
                
                # Handling Corrupt Frames
                if CorruptFrameStartTime is None:
                    CorruptFrameStartTime = time.time()
                else:
                    if (time.time() - CorruptFrameStartTime) >= MaxCorruptFrameDuration:
                        print("Corrupt frames received for over {} seconds.".format(MaxCorruptFrameDuration))
                        break

                # Enqueue the frame
                FrameQueue.put(Frame)

                cv2.imshow("Video", Frame)
                k = cv2.waitKey(1)
                if k == ord('q'):
                    break

            Video.release()
            cv2.destroyAllWindows()
            break  # Connection successful, exit the retry loop

        except Exception as e:
            logging.exception(e)
            Retries += 1
            time.sleep(RetryInterval)

    if Retries == MaxRetries:
        print("Failed to establish connection after {} Retries.".format(MaxRetries))
    else:
        print("Connection established successfully.")

# Define RTSP URL and call the function
RtspURL = "rtsp://admin:Sheraton123@10.111.111.106:554/Streaming/Channels/501/"

# Call the function with the RTSP URL
Connection(RtspURL)
