	from imutils.video import VideoStream
	import os
import numpy as np
import imutils
import time
import cv2

onPi = False

vs = VideoStream(usePiCamera=onPi, framerate=3).start()

#time.sleep(2.0)

people = {}

videoWidth = 1200
recordVideo = 0
videoText = ""

MODEL_FILE = "model.mdl"
path = 'data'

a = 0

def to_gray(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.equalizeHist(gray)
	return gray

def load_images(path):
	global people
	images, labels = [], []
	c = 0
	for dirname, dirnames, filenames in os.walk(path):
		for subdirname in dirnames:
			if not subdirname == 'ex':
				subjectPath = os.path.join(dirname, subdirname)
				#print str(c) + " - " + subdirname
				people[c] = subdirname
				for filename in os.listdir(subjectPath):
					file = os.path.join(subjectPath, filename)
					filename, file_extension = os.path.splitext(file)
					if file_extension == '.jpg':
						print(file)
						try:
							img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
							img = cv2.resize(img, (100,100))
							images.append(np.asarray(img, dtype=np.uint8))
							labels.append(c)
						except IOError, (errno, strerror):
							print "IOError({0}): {1}".format(errno, strerror)
						except:
							print "Unexpected error"
				c += 1
		print(people)
		return images, np.array(labels)

def detect(img, cascade):
	gray = to_grayscale(img)
	rects = cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

	if len(rects) == 0:
		return []
	return rects

def save_faces(path, cascade):
	images, labels = [], []
	c = 0
	#print "test " + path
	for dirname, dirnames, filenames in os.walk(path):
		for subdirname in dirnames:
			print str(c) + " - " + subdirname
			subjectPath = os.path.join(dirname, subdirname)
			for filename in os.listdir(subjectPath):
				try:
					filepath = os.path.join(subjectPath, filename)
					img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
					i = 1
					faces = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
					for face in faces:
						x, y, h, w = [result for result in face]
						cv2.imwrite(os.path.join(subjectPath, "face_") + filename + "_" + str(i) + ".jpg" ,img[y:y+h,x:x+w])
						i += 1
				except IOError, (errno, strerror):
					print "IOError({0}): {1}".format(errno, strerror)
				except:
					print "Unexpected error:"
					raise
			c += 1


def get_faces(img, cascade):
	return cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
	

def save_faces_img(prefix,img, cascade):
	global a
	faces = get_faces(img, cascade)
	c = 0
	for face in faces:
		x, y, h, w = [result for result in face]
		cv2.imwrite(prefix+str(a)+str(c)+".jpg",img[y:y+h,x:x+w])
		c += 1
	a = a + 1

def load_model(file=None):
	images, labels = load_images(path)
	#model = cv2.createFisherFaceRecognizer()
	model = cv2.createLBPHFaceRecognizer()
	if file != None:
		model.load(file)
		print "Trained model loaded."
	else:	
		model.train(images,labels)
		model.save(MODEL_FILE)
	return model

def train():
	return load_model()

def recognize(img, cascade, model):
	faces = get_faces(img, cascade)
	if len(faces)>0:
		i = 1
		for face in faces:
			x, y, h, w = [result for result in face]
			resized = cv2.resize(img[y:y+h,x:x+w], (100,100))
			recognized = model.predict(resized)
			return recognized
	return None, None


def draw_str(dst, (x, y), s):
	fontSize = 2.0
	textSize, baseline = cv2.getTextSize(s, cv2.FONT_HERSHEY_DUPLEX, fontSize, thickness = 2) 
	x = x - textSize[0]/2
	y = y - textSize[1]
	cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_DUPLEX, fontSize, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
	cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_DUPLEX, fontSize, (255, 255, 255), lineType=cv2.CV_AA)

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

#save_faces(path, faceCascade)

model = train()
#model = load_model(MODEL_FILE)

fourcc = cv2.cv.CV_FOURCC(*'MP4V')


video = None



while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = cv2.flip(frame,1)
	frame = imutils.resize(frame, width=videoWidth)

	if not videoText == "":
		draw_str(frame, (videoWidth/2,frame.shape[0]), videoText)

	#print(frame.shape)

	if recordVideo > 0:
		video.write(frame)
	

	# show the frame
	cv2.imshow("Hoosthere", frame)
	key = cv2.waitKey(1) & 0xFF


	if key == ord("q") or key == "q":
		break
	elif key == ord("d"):
		frame = to_gray(frame)
		save_faces_img("face", frame, faceCascade)
	elif key == ord("r") or key == "r":
		key = "q"
		recordVideo = 39
		
		try:
			os.remove('output.mp4')
		except OSError:
			pass

		video = cv2.VideoWriter('output.mp4', fourcc, 13.0, (videoWidth,450))

		frame = to_gray(frame)
		label, confidence = recognize(frame, faceCascade, model)


		if not label == None:
			videoText = people[label]
		else:
			videoText = "Not Found"

		print(videoText)

	if recordVideo == 1:
		video.release()
		video = None

	if recordVideo > 0:
		recordVideo = recordVideo - 1

	time.sleep(0.04)
