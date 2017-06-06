from PIL import Image
from PIL import ImageTk
import Tkinter as tki
import tkFont
import threading
import imutils
import time
import cv2
import os
import io
import subprocess
import boto3
import boto3.session
import bcssns as sns
import random
import cognitive_sr
import sound_recorder
import BingSpeechAPI as speech

class View:
	def __init__(self, vs, recognizer, network, width=320, height=450, framerate=32, videoduration=2):
		self.network = network
		self.state = 0

		self.voiceRecog = True

		self.session = boto3.session.Session(region_name='eu-central-1')
		self.s3 = boto3.resource('s3')
		self.videoS3Name = ''
		
		self.vs = vs
		self.outputPath = "outputPath"
		self.frame = self.vs.read()
		self.thread = None
		self.stopVideoLoop = None
		self.peopleCount = 0

		self.root = tki.Tk()
		self.root.resizable(width=False, height=False)
		self.root.geometry('{}x{}'.format(width, height))

		self.container = tki.Frame(self.root)
		self.container.pack(side="top", fill="both", expand=True)

		self.panel = None
		self.panelWidth = width

		self.framerate = framerate
		self.sleepduration = 1.0/self.framerate
		self.idleduration = 3*framerate
		self.idle = 0

		self.headerFont = tkFont.Font(family='Helvetica', size=130, weight='bold')
		self.subHeaderFont = tkFont.Font(family='Helvetica', size=20, weight='bold')
		self.subSHeaderFont = tkFont.Font(family='Helvetica', size=18, weight='bold')
		self.textFont = tkFont.Font(family='Helvetica', size=13, weight='normal')

		self.button = tki.Button(text=u"\u266C", command=self.ring, font=self.headerFont)
		self.buttonPacked = False

		self.textPanel = tki.Label(self.container, text="Hello, world", font=self.textFont)
		self.messageText = tki.Text(self.container, font=self.textFont, wrap=tki.WORD)

		self.stopVideoLoop = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		self.root.wm_title("Hoosthere")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.recognizer = recognizer

		self.videoText = None
		self.videoDuration = videoduration*self.framerate/3
		self.videoRecord = 0
		self.videoCodec = cv2.cv.CV_FOURCC(*'MJPG')
		self.video = None

		self.predictions = []

		self.message = ''

		self.recognizedPerson = -1
		self.catDetected = 0

		self.visitID = 0

		self.faceAuth = False

		self.testSentences = ['Be the change you wish to see in the world.', 'Don\'t count the days, make the days count!', 'It is not who I am underneath, but what I do that defines me.',
								'Only I can change my life. No one can do it for me.', 'The best preparation for tomorrow is doing your best today.']
		self.selectedTestSentence = 0	

		self.speech = speech.BingSpeechAPI()					
	def videoLoop(self):
		try:
			while (not self.stopVideoLoop.is_set()):
				if self.state == 0:
					self.peopleCount = 0
					if not self.buttonPacked:
						self.button.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						self.buttonPacked = True

					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					catCount, cats = self.recognizer.detect_cats(image)

					if catCount > 0:
						self.videoRecord = self.videoDuration
						self.catDetected = catCount
						print('INFO: Cat detected.')
						print('STATE: 0 -> 13')
						self.button.pack_forget()
						self.buttonPacked = False
						self.initVideo()
						self.state = 13

					time.sleep(self.sleepduration*3)
				elif self.state == 1:
					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)
					if not self.videoText == None:
						self.recognizer.draw_str(iframe, (self.panelWidth/2,iframe.shape[0]), self.videoText)
					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					faces = self.recognizer.detect_faces(image)

					if self.videoRecord == 0 and len(faces) > 0:
						self.videoRecord = self.videoDuration
						print('INFO: Started video recording.')

					self.peopleCount = max(len(faces), self.peopleCount)
					for face in faces:
						x0, y0, h, w = [result for result in face]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(0,234,12),1)

					catCount, cats = self.recognizer.detect_cats(image)
					for cat in cats:
						x0, y0, h, w = [result for result in cat]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(136,46,120),2)

					image = Image.fromarray(image)
					image = ImageTk.PhotoImage(image)
					
					if self.panel is None:
						self.textPanel['text'] = 'Please show \nyour face clearly. \nA green rectangle \nwill appear \naround your face.'
						self.textPanel['fg'] = '#a71c34'
						self.textPanel['font'] = self.textFont
						self.textPanel.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						self.panel = tki.Label(self.container,image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=0, pady=0)
					else:
						self.panel.configure(image=image)
						self.panel.image = image


					if self.videoRecord == 0 and len(faces) == 0:
						self.idle -= 1
						if self.idle%10 == 0:
							print('INFO: Idle ' + str(self.idle))
						if self.idle <= 0:
							self.state = 0
							self.panel.pack_forget()
							self.panel = None
							self.textPanel.pack_forget()
							self.buttonPacked = False
							print('INFO: Nobody is here.')
							print('STATE: 1 -> 0')


					if self.videoRecord != 0 and self.videoRecord%4 == 0 and self.peopleCount > 0:
						self.predictions.append(self.recognizer.recognize(self.frame))
						print('INFO: Calling recognize()')

					#Video Recording
					if (not self.video == None) and self.videoRecord > 0:

						self.videoRecord -= 1
						self.video.write(self.frame)

						if self.videoRecord <= 0:
							self.video.release()
							self.video = None
							print('INFO: Video saved.')
							#os.system('ffmpeg -i output.avi output.mp4')
							FNULL = open(os.devnull, 'w')
							subprocess.call('ffmpeg -i output.avi output.mp4', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
							FNULL = None
							print('INFO: Video conversion is completed.')

							#Moving to next state.
							self.panel.pack_forget()
							self.panel = None
							self.textPanel.pack_forget()
							print('STATE: 1 -> 2')
							self.state = 2
					time.sleep(self.sleepduration)
				elif self.state == 2:
					print('INFO: Uploading video.')

					self.textPanel['text'] = u"\u0489" + '\n\nProcessing...'
					self.textPanel['font'] = self.textFont
					self.textPanel.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)

					data = open('output.mp4', 'rb')
					self.videoS3Name = str(int(round(time.time() * 1000)))
					self.s3.Bucket('hoo-bucket').put_object(Key=self.videoS3Name + '.mp4', Body=data, ACL='public-read')
					data = None
					print('INFO: Video uploaded.')
					print('INFO: Video ID: ' + self.videoS3Name)
					print('INFO: Predictions: ')
					print(self.predictions)
					
					state = 2
					if self.peopleCount > 0:
						state, self.recognizedPerson = self.evalPredictions()
						self.peopleCount = 0
					else:
						state = 14

					self.peopleCount = 0
					self.catDetected = 0

					self.textPanel['text'] = ''
					self.textPanel.pack_forget()
					print('STATE: 2 -> ' + str(state))
					self.state = state
				elif self.state == 3:
					#Recognized check for message
					#self.recognizedPerson deletion

					if self.textPanel['text'] == '':
						self.textPanel['text'] = u"\u0489" + '\n\nProcessing...'
						self.textPanel['font'] = self.textFont
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					residentName = self.network.get_resident_name(self.recognizedPerson)

					if self.faceAuth:
						self.visitID = self.network.create_visit(self.recognizedPerson, self.videoS3Name, status=1)
						print('INFO: Posting visit to server.')
						print('INFO: Notification sent.')
						sns.send_push(body= residentName + ' has granted access via face recognition system.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
						sns.send_push(body= residentName + ' has granted access via face recognition system.', device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')

						print('STATE: 3 -> 31')
						self.state = 31
					else:
						self.textPanel['text'] = ''
						self.state = 4
						print('STATE: 3 -> 4')
				elif self.state == 31:
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()
					self.textPanel['text'] = 'Access Granted'
					self.textPanel['font'] = self.subHeaderFont
					self.textPanel['fg'] = '#26C281'
					self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					message_id, message = self.network.get_message(self.recognizedPerson)

					if message != None:
						self.network.update_message(message_id)
						self.messageText['bd'] = 0

						self.messageText.insert(tki.END, "There is a message for you:\n\n" + message)
						self.messageText['state'] = tki.DISABLED
						self.messageText.tag_configure("center", justify='center')
						self.messageText.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						time.sleep(8)

					time.sleep(5)
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()
					if message != None:
						self.messageText['state'] = tki.NORMAL
						self.messageText.delete(1.0, tki.END)
						self.messageText.pack_forget()
					self.catDetected = 0
					self.peopleCount = 0
					print('STATE: 31 -> 0')
					self.state = 0
				elif self.state == 4:
					# check for voice
					self.visitID = self.network.create_visit(self.recognizedPerson, self.videoS3Name, status=0)
					print('INFO: Posting visit to server.')
					residentName = self.network.get_resident_name(self.recognizedPerson)
					print('INFO: Notification sent.')
					sns.send_push(body= residentName + ' is at the door. Waiting for voice authentication.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
					sns.send_push(body= residentName + ' is at the door. Waiting for voice authentication.', device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')

					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Welcome\n' + residentName +'!\nYou will be\n directed to\n voice recognition.'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#000000'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					time.sleep(4)
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()
					print('STATE: 4 -> 41')
					self.state = 41
				elif self.state == 41:
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Please read\n the following\nsentence\n out loud.'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)
						self.selectedTestSentence = random.randint(0, len(self.testSentences))-1
						self.messageText.insert(tki.END, self.testSentences[self.selectedTestSentence])
						self.messageText['font'] = self.subSHeaderFont
						self.messageText['state'] = tki.DISABLED
						self.messageText.tag_configure("center", justify='center')
						self.messageText.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)


					success = True


					if self.voiceRecog:

						ms_list = self.network.microsoft_list()
						wav_path = 'sound_recog.wav'
						FNULL = open(os.devnull, 'w')
						subprocess.call('arecord -D plughw:1,0 -r 16000 -c 1 -d 5 -f S16_LE sound_recog.wav', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
						#	time.sleep(8)
						FNULL = None
						sentence = self.speech.recognize(wav_path)
						print('INFO: Sentence: ' + sentence)
						match = self.compareSentences(self.testSentences[self.selectedTestSentence], sentence)
						print(match)
						if match >= len(self.testSentences[self.selectedTestSentence].split(' '))/2:
							identification_result = self.identify_voice_profile('497d4917f97345fd9b6eb8368bfcf784', ms_list, wav_path)
							print('INFO: Voice recognition result: Profile ID:' + identification_result['identifiedProfileId'] + ' Confidence: ' + identification_result['confidence'])
							db_msID = self.network.get_resident_msID(self.recognizedPerson)
							if not identification_result['identifiedProfileId'] == db_msID:
								success = False
						else:
							success = False
					else:
						time.sleep(4)
					
					self.messageText['state'] = tki.NORMAL
					self.textPanel['text'] = ''
					self.messageText.delete(1.0, tki.END)
					self.messageText.pack_forget()

					status = self.network.visit_status(self.visitID)

					if status == 0:
						if success:
							print('STATE: 41 -> 43')
							self.state = 43
						else:
							print('STATE: 41 -> 44')
							self.state = 44
					else:
						if status == 1:
							self.textPanel['text'] = 'Access Granted'
							self.textPanel['font'] = self.subHeaderFont
							self.textPanel['fg'] = '#26C281'
						elif status == -1:
							self.textPanel['text'] = 'Access Rejected'
							self.textPanel['font'] = self.subHeaderFont
							self.textPanel['fg'] = '#D91E18'

						message_id, message = self.network.get_message(self.recognizedPerson)

						if message != None:
							self.network.update_message(message_id)
							self.messageText['bd'] = 0
							self.messageText.insert(tki.END, "There is a message for you:\n\n" + message)
							self.messageText['state'] = tki.DISABLED
							self.messageText.tag_configure("center", justify='center')
							self.messageText.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
							time.sleep(6)
							self.messageText['state'] = tki.NORMAL
							self.messageText.delete(1.0, tki.END)
							self.messageText.pack_forget()
						else:
							time.sleep(3)
						print('STATE: 41 -> 0')
						self.state = 0

					self.textPanel['text'] = ''
					self.textPanel.pack_forget()

				elif self.state == 43:
					if self.network.update_visit(self.visitID, 1):
						print('INFO: Visit updated.')
					print('INFO: Notification sent.')
					sns.send_push(body= residentName + ' has granted access via voice recognition system.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
					sns.send_push(body= residentName + ' has granted access via voice recognition system.', device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')
					print('STATE: 43 -> 31')
					self.state = 31
				elif self.state == 44:
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'We can\'t\n recognize\nyour voice.'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)
						print('INFO: Person is not authorized via Voice Recognition.')
						time.sleep(3)

					residentName = self.network.get_resident_name(self.recognizedPerson)
					msg = residentName + ' couldn\'t pass voice recognition control. Waiting for your response.'
					print('INFO: Notification sent.')
					sns.send_push(body= msg, device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
					sns.send_push(body= msg, device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')

					self.textPanel['text'] = ''
					self.textPanel.pack_forget()

					print('STATE: 44 -> 6')
					self.state = 6

				elif self.state == 5:
					self.textPanel['text'] = ''
					self.idle = self.idleduration/2
					self.textPanel.pack_forget()
					sns.send_push(body= 'There is someone at your door.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
					sns.send_push(body= 'There is someone at your door.', device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')
					self.visitID = self.network.create_visit(self.recognizedPerson, self.videoS3Name)

					print('INFO: Visit created.')
					print('STATE: 5 -> 6')
					self.state = 6
				elif self.state == 6:
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Waiting\nfor response\n from\n a resident.'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#000000'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					message_id, message = self.network.get_message(self.recognizedPerson)

					if message != None:
						self.network.update_message(message_id)
						self.messageText['bd'] = 0
						self.messageText.insert(tki.END, "There is a message for you:\n\n" + message)
						self.messageText['state'] = tki.DISABLED
						self.messageText.tag_configure("center", justify='center')
						self.messageText.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						time.sleep(6)
						self.messageText['state'] = tki.NORMAL
						self.messageText.delete(1.0, tki.END)
						self.messageText.pack_forget()

					self.idle -= 1

					semiidle = self.idleduration/2

					if self.idle%10 == 0:
						print('INFO: Idle ' + str(self.idle))
						
					if self.idle == semiidle:
						residentName = self.network.get_resident_name(self.recognizedPerson)
						msg = residentName + ' is still waiting for your response.'
						sns.send_push(body= msg, device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
						sns.send_push(body= msg, device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')
						print('INFO: Reminding notification sent.')

					if self.idle <= 0:
						if self.network.update_visit(self.visitID, -1):
							print('INFO: Visit updated.')
						self.textPanel['text'] = 'No Response'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)
						time.sleep(5)
						self.textPanel['text'] = ''
						self.textPanel.pack_forget()
						print('INFO: No response from owner')
						print('STATE: 6 -> 0')
						self.state = 0
						continue

					status = self.network.visit_status(self.visitID)
					if status == 1:
						self.textPanel['text'] = 'Access Granted'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#26C281'
					elif status == -1:
						self.textPanel['text'] = 'Access Rejected'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#D91E18'

					if (status is not None) and (not status == 0):
						time.sleep(5)
						self.textPanel['text'] = ''
						self.textPanel.pack_forget()
						print('STATE: 6 -> 0')
						self.state = 0
					else:
						time.sleep(self.sleepduration*5)

				elif self.state == 10:
					#access granted check w/wo message
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Access Granted'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#26C281'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					time.sleep(5)
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()

					print('STATE: 10 -> 0')
					self.state = 0
				elif self.state == 13:
					#TODO cat notif

					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)
					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					catCount, cats = self.recognizer.detect_cats(image)
					for cat in cats:
						x0, y0, h, w = [result for result in cat]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(136,46,120),2)

					image = Image.fromarray(image)
					image = ImageTk.PhotoImage(image)
					
					if self.panel is None:
						self.panel = tki.Label(self.container,image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=0, pady=0)
					else:
						self.panel.configure(image=image)
						self.panel.image = image

					if (not self.video == None) and self.videoRecord > 0:
						self.videoRecord -= 1
						self.video.write(self.frame)

						if self.videoRecord <= 0:
							self.video.release()
							self.video = None
							print('INFO: Video saved.')
							#os.system('ffmpeg -i output.avi output.mp4')
							FNULL = open(os.devnull, 'w')
							subprocess.call('ffmpeg -i output.avi output.mp4', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
							FNULL = None
							print('INFO: Video conversion is completed.')

							#Moving to next state.
							self.panel.pack_forget()
							self.panel = None
							print('STATE: 13 - > 2')
							self.state = 2
					time.sleep(self.sleepduration)
				elif self.state == 14:
					#access granted check w/wo message
					self.network.create_visit('cat', self.videoS3Name, status=1)
					sns.send_push(body= 'Cat is home.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
					sns.send_push(body= 'Cat is home.', device_id = '119c70f2e039960b82a9a6b74eb6db172420e0e3445c579675400abd19c08545')
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Cat\nAccess\nGranted'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#882E78'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					time.sleep(5)
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()

					print('STATE: 14 -> 0')
					self.state = 0
				else:
					print(212)
					time.sleep(5)

		except RuntimeError, e:
			print("INFO: caught a RuntimeError")

	def ring(self):
		self.state = 1
		self.idle = self.idleduration*3/2
		self.button.pack_forget()
		self.buttonPacked = False
		self.initVideo()
		print('INFO: Ringed the bell!')

	def onClose(self):
		print("INFO: Closing")
		self.stopVideoLoop.set()
		self.vs.stop()
		#self.root.destroy()
		self.root.quit()

	def initVideo(self):

		try:
			os.remove('output.avi')
			os.remove('output.mp4')
		except OSError:
			pass

		self.video = cv2.VideoWriter('output.avi', self.videoCodec, self.framerate/5, (self.frame.shape[1],self.frame.shape[0]))

	def evalPredictions(self, picthreshold=85, voicethreshold=90):
		picMul = 0.5
		voiceMul = 0.5
		scoresPic = {}
		scoresVoice = {}

		state = -1
		person = -1
		numInstance = len(self.predictions)
		picMul = int(picMul*numInstance)
		voiceMul = int(voiceMul*numInstance)

		for ps in self.predictions:
			for p in ps:
				if p[1] < picthreshold:
					if not p[0] in scoresPic.keys():
						scoresPic[p[0]] = 1
					else:
						scoresPic[p[0]] += 1
				elif p[1] < voicethreshold:
					if not p[0] in scoresVoice.keys():
						scoresVoice[p[0]] = 1
					else:
						scoresVoice[p[0]] += 1

		self.predictions = []

		if len(scoresPic) == 0 and len(scoresVoice) == 0:
			print('INFO: Unauthorized visitor.')
			state = 5
			return state, 'unknown'

		maxID = -1
		if len(scoresPic) > 0:
			maxIndex = scoresPic.values().index(max(scoresPic.values()))
			maxID = scoresPic.keys()[maxIndex]
		elif len(scoresVoice) > 0:
			maxIndex = scoresVoice.values().index(max(scoresVoice.values()))
			maxID = scoresVoice.keys()[maxIndex]
				
		person = maxID
		if (person in scoresPic.keys()) and  (scoresPic[person] >= picMul):
			state = 3
		else:
			tot = 0
			if (person in scoresPic.keys()):
				tot += scoresPic[person]
			if (person in scoresVoice.keys()):
				tot += scoresVoice[person]
			if tot >= voiceMul:
				state = 4
			else:
				person = -1
				state = 5
		
		if person == -1:
			return state, 'unknown'
		
		return state, self.recognizer.people[person]

	def identify_voice_profile(self, subscription_key, profile_ids, wav_path):
		""" identifies a profile using a wav recording of them speaking """
		with io.open(wav_path, 'rb') as wav_file:
			wav_data = wav_file.read()

		speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
		result = speech_identification.identify_profile(
			profile_ids.split(','), wav_data, short_audio=True)
		return result

	def compareSentences(self, s1, s2):
		match = {}
		s1words = s1.lower().split(' ')
		s2words = s2.lower().split(' ')
		for w1 in s1words:
			for w2 in s2words:
				if w1 == w2:
					match[w1] = 1
					break

		return len(match)
