# USAGE
# python client.py --server-ip SERVER_IP

# import the necessary packages
from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=False,
                help="ip address of the server to which the client will connect",
                default='tcp://127.0.0.1:5555')
ap.add_argument("-a", "--area", required=False, default="area1")
args = vars(ap.parse_args())

# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="{}".format(
    args["server_ip"]))

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = args["area"]
# vs = VideoStream(usePiCamera=True).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)
count = 0

while True:
    # read the frame from the camera and send it to the server
    print(count)
    count += 1
    frame = vs.read()
    sender.send_image(rpiName, frame)
