#Import necessary libraries
from flask import Flask, render_template, Response, redirect, stream_with_context
from flask.helpers import url_for
import cv2
import time
import os
import HandTrackingModule as htm
#Initialize the Flask app
app = Flask(__name__)

#images from folder
globalTotalFingers = -1
folderPath = "FingerImages"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    # print(f'{folderPath}/{imPath}')
    overlayList.append(image)


camera1 = cv2.VideoCapture(0)

pTime = 0

detector = htm.handDetector(detectionCon=0.75)

tipIds = [4, 8, 12, 16, 20]

@app.route('/camera.html')
def camera():
    return render_template('camera.html')
"""def youtubeUrlFor():
    return render_template('youtube.html')
@app.route('/youtuberedirect')
def youtubeRedirect():
    return redirect('https://www.youtube.com/')
@app.route('/mailRedirect')
def mailRedirect():
    return redirect('https://mail.google.com/mail/u/0/#inbox')"""

def gen_frames():  
    while True:
        success, frame = camera1.read()  # read the camera frame
        if not success:
            break
        else:
            frame = detector.findHands(frame)
            lmList = detector.findPosition(frame, draw=False)

            if len(lmList) != 0:
                fingers = []

                # Thumb
                if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                 # 4 Fingers
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # print(fingers)
                totalFingers = fingers.count(1)
                h, w, c = overlayList[totalFingers - 1].shape
                frame[0:h, 0:w] = overlayList[totalFingers - 1]
                print(totalFingers)
                global globalTotalFingers
                globalTotalFingers = totalFingers
                cv2.rectangle(frame, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN,
                        10, (255, 0, 0), 25)
                
                
                global pTime
                cTime = time.time()
                fps = 1 / (cTime - pTime)
                pTime = cTime
                #fps = 0
                cv2.putText(frame, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                            3, (255, 0, 0), 3)
                """if totalFingers == 1:
                    youtubeRedirect()"""

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            

def get_fingers():
    yield str(globalTotalFingers)
@app.route('/video_result')
def video_result():
    print('console',globalTotalFingers)
    """if globalTotalFingers == 1:
        youtubeUrlFor()"""
    return Response(stream_with_context(get_fingers()),mimetype='text')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)