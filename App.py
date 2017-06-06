from Recognizer import Recognizer
from imutils.video import VideoStream
from View import View
import argparse
import time
from Network import Network

#Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=1,
	help="Use Raspberry Camera")
ap.add_argument("-w", "--width", type=int, default=316,
	help="Witdh of the window")
ap.add_argument("-ht", "--height", type=int, default=450,
	help="Height of the window")
ap.add_argument("-fr", "--framerate", type=int, default=25,
	help="Frame rate of the camera")
opt = vars(ap.parse_args())


#recognizer = Recognizer()
recognizer = Recognizer(modelFile='model.mdl')
network = Network()
#network = Network(endpoint='http://localhost:8000/hoo/')
print('INFO: People: ')
print(recognizer.people)

print("INFO: Launching camera")
vs = VideoStream(usePiCamera=opt["picamera"] > 0).start()
time.sleep(2.0)
view = View(vs, recognizer, network, width=opt["width"], height=opt["height"], framerate=opt["framerate"])


print("INFO: Application started successfully.")
view.root.mainloop()
