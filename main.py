#Classes
from gestures.gesture import Hand
from Util import print_error, print_success
from config import DEBUG, MODEL_PATH

#Libs
import time
import cv2

#Mediapipe imports
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
MP_HANDS = mp.solutions.hands
MP_DRAWING = mp.solutions.drawing_utils
MP_DRAWING_STYLES = mp.solutions.drawing_styles


#Init webcam window
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 550)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
if DEBUG:
    cv2.namedWindow("Handflow - Debug", cv2.WINDOW_NORMAL )


#---- SETUP MEDIAPIPE LIVE-STREAM MODE ----
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

recognition_frame = None
recognition_result_list = []
# Create a gesture recognizer instance with the live stream mode:
def save_result(result: vision.GestureRecognizerResult, unused_output_image: mp.Image, timestamp_ms: int):
  recognition_result_list.append(result)

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.8,
    min_tracking_confidence=0.8,
    num_hands=1, #num_hands=2,
    result_callback=save_result)
#---------------------------------------------

def main():
    #Start recognizer
    with GestureRecognizer.create_from_options(options) as recognizer:
        print_success("Recognizer loaded!")

        #Capture loop
        while cap.isOpened():
            #Read frame
            success, image = cap.read()
            if not success:
                print_error("OpenCV error! Try restarting.")
                exit(1)
            if DEBUG:
                cv2.resizeWindow("Handflow - Debug", 600, 400)

            # Convert the image from BGR to RGB as required by the TFLite model.
            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

            # Run gesture recognizer using the model.
            recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)
            current_frame = image

            #If recognized gesture
            if recognition_result_list:
                r_hand = None
                if len(recognition_result_list[0].hand_landmarks) > 0:
                    r_hand = Hand(recognition_result_list[0].hand_landmarks, recognition_result_list[0].gestures)
                    r_hand.make_gesture()

                text_offset = 0
                #For each hand, print position, gesture and draw landmarks
                for hand_index, hand_landmarks in enumerate(recognition_result_list[0].hand_landmarks):
                    handpos = r_hand.get_handpos(hand_index) # Get position
                    handgest = r_hand.get_hand_gesture(hand_index) # Get gesture

                    #Draw coords
                    cv2.putText(current_frame, f"x: {round(handpos.x, 2)} y: {round(handpos.y, 2)}", (10, 30+text_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (204, 71, 102), 2, cv2.LINE_AA)
                    #Display gesture
                    cv2.putText(current_frame, handgest, (10, 80+text_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (51, 153, 51), 2, cv2.LINE_AA)

                    text_offset += 200

                    #--- DRAW LANDMARKS ---
                    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                    hand_landmarks_proto.landmark.extend([
                        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y,
                                                        z=landmark.z) for landmark in
                        hand_landmarks
                    ])
                    MP_DRAWING.draw_landmarks(
                        current_frame,
                        hand_landmarks_proto,
                        MP_HANDS.HAND_CONNECTIONS,
                        MP_DRAWING_STYLES.get_default_hand_landmarks_style(),
                        MP_DRAWING_STYLES.get_default_hand_connections_style())
                    #---     ------     ---

                #Update frame
                recognition_frame = current_frame
                recognition_result_list.clear()

                #Show
                if recognition_frame is not None and DEBUG:
                    cv2.imshow("Handflow - Debug", recognition_frame)

            # Stop the program if the ESC key is pressed.
            if cv2.waitKey(1) == 27:
                break

if __name__ == "__main__":
    main()
