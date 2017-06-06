from imutils.video import VideoStream
import os
import numpy as np
import imutils
import time
import cv2
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=1,
	help="Use Raspberry Camera")
ap.add_argument("-w", "--width", type=int, default=500,
	help="Witdh of the window")
ap.add_argument("-ph", "--path", type=str, default='data/new/',
	help="Image collection path.")
opt = vars(ap.parse_args())

vs = VideoStream(usePiCamera=opt["picamera"] > 0).start()

#time.sleep(2.0)
videoWidth = opt["width"]

path = opt["path"]

if not os.path.isdir(path):
	os.makedirs(path)


def to_gray(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#gray = cv2.equalizeHist(gray)
	return gray



def get_faces(img, cascade):
	return cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
	

def save_faces_img(path, img, cascade):
	faces = get_faces(img, cascade)
	for face in faces:
		x, y, h, w = [result for result in face]
		name = str(int(round(time.time() * 1000)))
		name = path+name+".jpg"
		cv2.imwrite(name,img[y:y+h,x:x+w])

loop = True

def click(event, x, y, flags, param):
	global loop
	loop = False

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

a = 0



cv2.namedWindow("Hoosthere Face Collection")
cv2.setMouseCallback("Hoosthere Face Collection", click)

while loop:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = cv2.flip(frame,1)
	frame = imutils.resize(frame, width=videoWidth)

	#print(frame.shape)
	

	# show the frame
	cv2.imshow("Hoosthere Face Collection", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q") or key == "q":
		break

	if a%10 == 0:
		frame = to_gray(frame)
		save_faces_img(path, frame, faceCascade)
	

	time.sleep(0.04)
	a += 1

cv2.destroyAllWindows()