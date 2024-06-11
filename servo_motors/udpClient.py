import time
import socket
import struct

#UPD Client to send data to a MCU in order to move 2 servo motors
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)

def move_servo(deg):
    data = struct.pack('ff', deg.x, deg.y)
    addr = ("addr", 5005)
    client_socket.sendto(data, addr)