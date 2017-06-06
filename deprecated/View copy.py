from Recognizer import Recognizer
from PIL import Image
from PIL import ImageTk
import Tkinter as tki
import threading
import imutils
import time
import cv2

class MainView:
	def __init__(self, vs, width=320, height=450, framerate=32):
		self.vs = vs

		self.root = tki.Tk()

		self.framerate = framerate
		self.sleepduration = 1.0/self.framerate
		self.frame = None
		self.thread = None
		self.stopEvent = None

		self.root.resizable(width=False, height=False)
		self.root.geometry('{}x{}'.format(width, height))

		self.panelWidth = width

		self.panel = None

		self.button = tki.Button(self.root, text="Ring the Bell!", command=self.ring)
		self.button.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

		self.stopVideoLoop = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		self.root.wm_title("Hoosthere")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.recognizer = Recognizer()

	def videoLoop(self):
		try:
			while not self.stopVideoLoop.is_set():
				self.frame = self.vs.read()
				self.frame = cv2.flip(self.frame,1)
				self.frame = imutils.resize(self.frame, width=self.panelWidth)

				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)

				if self.panel is None:
					self.panel = tki.Label(image=image, master=self.root)
					self.panel.configure(image=image)
					self.panel.imgtk = image
					self.panel.pack()
				else:
					self.panel.imgtk = image
					self.panel.configure(image=image)

				time.sleep(self.sleepduration)
		except RuntimeError, e:
			print("[INFO] Runtime Error")
	
	def ring(self):
		print('Ringed the bell!')
		print(self.recognizer.people[self.recognizer.recognize(self.frame)[0]])
		return 0

	def onClose(self):
		print("[INFO] Closing")
		self.stopVideoLoop.set()
		self.vs.stop()
		self.root.quit()
		self.root.destroy()