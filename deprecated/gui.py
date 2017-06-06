#importing modules required
from ttk import *
import Tkinter as tk
from Tkinter import *
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
import imutils
from imutils.video import VideoStream


global last_frame                                      #creating global variable
last_frame = np.zeros((480, 640, 3), dtype=np.uint8)
global cap
cap = VideoStream(usePiCamera=False).start()

def show_vid():                        
    frame = cap.read()
    frame = cv2.flip(frame, 1)

    global last_frame
    last_frame = frame.copy()

    pic = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)     #we can change the display color of the frame gray,black&white here
    img = Image.fromarray(pic)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_vid)

if __name__ == '__main__':
    root=tk.Tk()                                     #assigning root variable for Tkinter as tk
    lmain = tk.Label(master=root)
    lmain.grid(column=0, rowspan=4, padx=5, pady=5)
    button = tk.Button(root, text="Ring the Bell!")
    button.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

    root.title("Sign Language Processor")            #you can give any title
    show_vid()
    root.mainloop()                                  #keeps the application in an infinite loop so it works continuosly
    cap.release()