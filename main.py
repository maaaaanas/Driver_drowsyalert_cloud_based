import cv2
import numpy as np
import pygame
import os
import time
import requests
last_alert_time = 0


EYE_CLOSED_FRAMES_THRESHOLD = 15
ALARM_FILE = os.path.join("assets", "alarm.wav")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

def get_working_camera():
    print("[INFO] Searching for working camera...")
    for i in range(3):
        cap = cv2.VideoCapture(i)
        time.sleep(1)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"[INFO] Camera found at index {i}")
                return cap
        cap.release()
    print("[ERROR] No working camera found.")
    return None

# -------- CLOUD + SMS ALERT --------
def send_cloud_alert(driver_id="D001", vehicle="Car-1"):
    try:
        data = {
            "driver_id": driver_id,
            "status": "DROWSY",
            "vehicle": vehicle
        }
        r = requests.post("http://127.0.0.1:5000/alert", json=data)
        print("[CLOUD] Alert sent:", r.text)
    except Exception as e:
        print("[CLOUD ERROR]", e)


def main():
    print("[INFO] Driver Drowsiness Detection Started (Python 3.13 Safe Mode)")

    # Safe audio init
    try:
        pygame.mixer.init()
        alarm_sound = pygame.mixer.Sound(ALARM_FILE)
        audio_ok = True
        print("[INFO] Alarm audio initialized.")
    except Exception as e:
        print("[WARNING] Audio failed:", e)
        audio_ok = False

    cap = get_working_camera()
    if cap is None:
        return

    closed_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Camera frame not received.")
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        status_text = "NO FACE"
        status_color = (0, 255, 255)

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]

                eyes = eye_cascade.detectMultiScale(roi_gray)

                if len(eyes) == 0:
                    closed_frames += 1
                else:
                    closed_frames = 0

                if closed_frames >= EYE_CLOSED_FRAMES_THRESHOLD:
                    status_text = "DROWSY! WAKE UP!"
                    status_color = (0, 0, 255)
                    if audio_ok:
                        alarm_sound.play()
                else:
                    status_text = "AWAKE"
                    status_color = (0, 255, 0)
                    if audio_ok:
                        alarm_sound.stop()

                break
        else:
            closed_frames = 0
            if audio_ok:
                alarm_sound.stop()

        cv2.rectangle(frame, (0, 0), (frame.shape[1], 60), (0, 0, 0), -1)
        cv2.putText(frame, f"Status: {status_text}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

        cv2.imshow("Driver Drowsiness Detection - Python 3.13", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if audio_ok:
        pygame.mixer.quit()

if __name__ == "__main__":
    main()
