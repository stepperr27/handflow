import sys
from Util import print_error
from config import SCROLLING_SPEED, STABILIZATION

#Multiplaform modules
from pynput.mouse import Button, Controller
import pyautogui

class OSHandler():
    def __init__(self) -> None:
        self.__screen_size = pyautogui.size() #Get screen size
        self.Width = self.__screen_size.width 
        self.Height = self.__screen_size.height
        self.__Mouse = Controller() #Get mouse controller
        self.__isMousePressed = False #Mouse pressed toggle
        self.__last_pos = [] #Stores last registered positions


    #Stabilization alorithm
    def is_hand_moving(self, coords):
        if STABILIZATION:
            if len(self.__last_pos) > 20:
                self.__last_pos.clear()
            
            #Add entry to list
            self.__last_pos.append(coords)
            
            #Find x and y max
            x_max = max(self.__last_pos, key=lambda item: item.x)
            y_max = max(self.__last_pos, key=lambda item: item.y)

            #Find x and y min
            x_min = min(self.__last_pos, key=lambda item: item.x)
            y_min = min(self.__last_pos, key=lambda item: item.y)

            #Check if hand is moving
            if ((x_max.x - x_min.x) <= 0.008) and ((y_max.y - y_min.y) <= 0.008):
                return False
            else:
                return True
        else:
            return False
        

    #None - Realse mouse
    def mouse_release(self):
        self.__Mouse.release(Button.left)
        self.__isMousePressed = False


    #Move cursor to x, y coords - Open gesture
    def move_cursor(self, coords):
        if self.__isMousePressed:
            self.mouse_release()
        
        if (self.is_hand_moving(coords)):
            self.__Mouse.position = (round(coords.x*self.Width), round(coords.y*self.Height))


    #Move cursor while pressing the left mouse button - Point gesture
    def mouse_click(self, coords):
        if (self.is_hand_moving(coords)):
            self.__Mouse.position = (round(coords.x*self.Width), round(coords.y*self.Height))
        
        if not self.__isMousePressed:
            self.__Mouse.press(Button.left)
            self.__isMousePressed = True


    #Scroll up
    def scroll_up(self):
        if self.__isMousePressed:
            self.mouse_release()
        self.__Mouse.scroll(0, SCROLLING_SPEED)


    #Scroll down
    def scroll_down(self):
        if self.__isMousePressed:
            self.mouse_release()
        self.__Mouse.scroll(0, SCROLLING_SPEED * -1)


    #Move active window - Fist gesture
    def move_window(self, coords):
        #Detect OS
        if self.__isMousePressed:
            self.mouse_release()

        if (self.is_hand_moving(coords)):

            #Linux
            if 'linux' in sys.platform:
                pass #Not implemented yet

            #MacOS
            elif 'darwin' in sys.platform:
                from AppKit import NSWorkspace
                from ScriptingBridge import SBApplication

                bundleID = (NSWorkspace.sharedWorkspace() .activeApplication()['NSApplicationBundleIdentifier']) #Get bundleID (working only for OS apps)
                try:
                    app = SBApplication.applicationWithBundleIdentifier_(bundleID)
                    app_wind = app.windows()[0]
                    #Move window
                    app_wind.setPosition_([round(coords.x*self.Width)-self.Width/2, round(coords.y*self.Height)-self.Height/2])
                except:
                    pass
            
            #Windows
            elif 'win32' in sys.platform:
                import win32gui

                #Get window
                hwnd = win32gui.GetForegroundWindow()
                if len(win32gui.GetWindowText(hwnd)) == 0:
                    return

                rect = win32gui.GetWindowRect(hwnd)
                win_x = rect[0]
                win_y = rect[1]
                w_width = rect[2] - win_x
                h_width = rect[3] - win_y
                #Move window
                win32gui.MoveWindow(hwnd, int(round(coords.x*self.Width)-w_width/2), int(round(coords.y*self.Height)-h_width/2), w_width, h_width, True)

            else:
                print_error("OS not supported!")
                exit(1)