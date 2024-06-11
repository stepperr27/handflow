from gestures import OSHandler
os_handler = OSHandler()

#Point utility
class Point:
    def __init__(self, coord_x, coord_y):
        self.x = coord_x
        self.y = coord_y

#--- Hand class ---
class Hand:

    #Constructor 
    def __init__(self, hand_landmarks, gestures):
        self.hand_landmarks = hand_landmarks #Landmarks
        self.gestures = gestures #Gesture detected
        self.num_hands = len(self.hand_landmarks) #Num hands detected


    #Get hand postion by finding the center of the palm
    def get_handpos(self, hand_id=0):
        p0 = Point(self.hand_landmarks[hand_id][0].x, self.hand_landmarks[hand_id][0].y)
        p9 = Point(self.hand_landmarks[hand_id][9].x, self.hand_landmarks[hand_id][9].y)

        #Find the palm center
        coord_x = (p0.x + p9.x)/2
        coord_y = (p0.y + p9.y)/2

        #Normalize to reach all screen coords
        _x = (1.282051282051282 * coord_x -0.15384615384615383) #Restrict x-axis area (from 0.12 to 0.9)
        _y = (1.5625 * coord_y -0.25) #Restrict y-axis area (from 0.08 to 0.9)

        #Return coords
        return Point(_x, _y)
    

    #Check if the index tip is above the middle of the mouse
    #Define if is up or down
    def is_scrollingup(self, hand_id=0):
        p8_y = self.hand_landmarks[hand_id][8].y
        p5_y = self.hand_landmarks[hand_id][5].y

        if p8_y > p5_y:
            return True
        else:
            return False
    

    #Get gesture name
    def get_hand_gesture(self, hand_id=0):
        #Get gesture classification results
        category_name = self.gestures[hand_id][0].category_name
        score = round(self.gestures[hand_id][0].score, 2)
        return f'{category_name} ({score})'
    
    
    #Execute action associated with gesture
    def make_gesture(self):
        coords = self.get_handpos(0) #Only 1 hand enabled - high resources consumption
        category_name = self.gestures[0][0].category_name #Get gesture name

        if category_name == "pinch":
            os_handler.mouse_click(coords) #Click

        elif category_name == "open":
            os_handler.move_cursor(coords) #Move

        elif category_name == "scroll":
            if (self.is_scrollingup(0)):
                os_handler.scroll_up() #Scroll up
            else:
                os_handler.scroll_down() #Scroll up

        elif category_name == "fist":
            os_handler.move_window(coords) #Move window

        else:
            os_handler.mouse_release()

    
    