#Run on a microcontroller with circuit python!

import time, wifi, socketpool
import board
import pwmio
import struct
from adafruit_motor import servo


#Wifi creds
SSID = ""
PASSWORD = ""
#Pins
PIN_Y_SERVO = board.GP4
PIN_X_SERVO = board.GP5


#Init servos
pwm_x = pwmio.PWMOut(PIN_X_SERVO, duty_cycle=2 ** 15, frequency=50)
pwm_y = pwmio.PWMOut(PIN_Y_SERVO, duty_cycle=2 ** 15, frequency=50)
x_axis_servo = servo.Servo(pwm_x)
y_axis_servo = servo.Servo(pwm_y)

#Init WIFI
print("[!] Connecting to WiFi...")
wifi.radio.connect(ssid=SSID, password=PASSWORD)
print("[!] IP addr: ", wifi.radio.ipv4_address)
pool = socketpool.SocketPool(wifi.radio)

udp_host = str(wifi.radio.ipv4_address)
udp_port = 5005
udp_buffer = bytearray(8) # Store our incoming packet

sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM) # UDP socket
sock.bind((udp_host, udp_port))

print("> Listening on: ",udp_host, udp_port)
while True:
    size, addr = sock.recvfrom_into(udp_buffer)
    coords = struct.unpack('ff', udp_buffer) #Unpack floats and move servo
    x = coords[0]
    y = coords[0]
    x_axis_servo.angle = x * 180
    y_axis_servo.angle = y * 180

