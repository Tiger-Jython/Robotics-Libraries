import music
_g1=['c6:1','r','c6,1','r','r','r']
def setAlarm(on):
	if on:music.play(_g1,wait=False,loop=True)
	else:music.stop()
def beep():music.pitch(2000,200,wait=False)