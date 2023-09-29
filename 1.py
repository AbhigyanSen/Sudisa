import cv2
import time
import logging

# Establish Connection
def Connection(RtspURL, MaxRetries=3, RetryInterval=10, MaxCorruptFrameDuration=30):
    Retries = 0
    CorruptFrameStartTime = None

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