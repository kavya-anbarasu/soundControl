# #GoodOne
import pyaudio
import wave
import audioop
import osascript
import re
import subprocess
import time
import tkinter
from tkinter import *
import threading

CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
boolean = True
stream = None

def outputVolume():
    """
    Get the current speaker output volume from 0 to 100.

    Note that the speakers can have a non-zero volume but be muted, in which
    case we return 0 for simplicity.

    Note: Only runs on macOS.
    """
    cmd = "osascript -e 'get volume settings'"
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = process.stdout.strip().decode('ascii')

    pattern = re.compile(r"output volume:(\d+), input volume:(\d+), "
                         r"alert volume:(\d+), output muted:(true|false)")
    volume, _, _, muted = pattern.match(output).groups()

    volume = int(volume)
    muted = (muted == 'true')

    return 0 if muted else volume

def determineBaseline(stream):
	print("Determining Baseline...")
	sum = 0
	for i in range(0, 200):
		data = stream.read(CHUNK)
		rms = audioop.rms(data, 2)   # here's where you calculate the volume
		sum += rms
	avg = sum/500
	return (avg)

def adjustVolume(currentVol, rms, THRESHOLD):
	#This is percent increase of background noise compared to the threshold
	increaseInput = (rms - THRESHOLD)/THRESHOLD
	decreaseVol = 1 - increaseInput
	newVol = decreaseVol * currentVol

	for i in range(int(currentVol), int(newVol), -10):
		osascript.osascript("set volume output volume " + str(i))

def resetOriginalVol(rms, THRESHOLD):
	start = time.time()

	flag = True
	while time.time() - start < 5:
		if rms > THRESHOLD:
			flag = False
	return flag

class audioProccessor(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		main()
		

def main():
	global boolean 
	global stream 

	ORIGINAL_VOLUME = outputVolume()

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		frames_per_buffer=CHUNK)

	BASELINE = determineBaseline(stream)
	print(BASELINE)
	#THRESHOLD = BASELINE * 4
	THRESHOLD = 1200 + BASELINE
	
	print("Button clicked.")
	#for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	while boolean == True:
		data = stream.read(CHUNK, False)
		rms = audioop.rms(data, 2)   # here's where you calculate the volume

		time.sleep(.1)
		print (rms)
		if rms > THRESHOLD:
			adjustVolume(ORIGINAL_VOLUME, rms, THRESHOLD)
			if resetOriginalVol(rms, THRESHOLD) == True:
				for i in range(int(currentVol), int(ORIGINAL_VOLUME), 10):
					osascript.osascript("set volume output volume " + str(i))

	stream.stop_stream()
	stream.close()
	p.terminate()	


def startClicked():
	audioProccessor().start()

def close():
	global boolean
	print("working?")
	boolean = False
	exit()


window = Tk()
window.title("Music Controller")
window.geometry("350x200")

startButton = Button(window, text = "Start", height = 5, width = 10, highlightbackground='#3E4149', command = startClicked)
startButton.grid(column = 1, row = 0)
startButton.place(relx=0.5, rely=0.25, anchor=CENTER)

stopButton = Button(window, text = "Stop", height = 5, width = 10, highlightbackground='#3E4149', command = close)
stopButton.grid(column = 1, row = 0)
stopButton.place(relx=0.5, rely=0.75, anchor=CENTER)

window.mainloop()




   
'''count = 0
for i in range(0, 500):
	data = stream.read(CHUNK)
	rms = audioop.rms(data, 2)
	count += 1
print (count)'''
