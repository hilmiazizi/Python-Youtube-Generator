#!python3
import os
from moviepy.editor import *
from colorama import Fore, init
from mutagen.wave import WAVE
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import json
import moviepy.audio.fx.all as afx

init(autoreset=True)
os.system('cls')


def CheckFile():
	from os.path import isfile as validate
	print('[+] Checking Image Resource')
	trigger = False
	config = open('config.json').read()
	config = json.loads(config)
	path = './config/image/'
	for i in range(len(config['image'])):
		image = config['image'][i]
		check = validate(path+image)
		if not check:
			print('[-] File not found : ',image)
			trigger = True
	for index in config['section']:
		content = index['image']
		for image in content:
			check = validate(path+image)
			if not check:
				print('[-] File not found : ',image)
				trigger = True
	return trigger

def BackSound(duration):
	bgsd = AudioFileClip('./lib/bgsound.mp3').set_duration(duration).volumex(0.35)
	return(bgsd)

def Assets():
	opening = VideoFileClip('./lib/opening.mp4').set_fps(30).resize((1280,720))
	transition = VideoFileClip('./lib/transition.mp4').set_fps(30).resize((1280,720))
	return opening, transition

def addoverlay(text, duration):
	bg = ImageClip('./lib/ovr.png').set_fps(30).set_duration(duration).resize((1280,720))
	txt_clip = TextClip(text, fontsize = 45, color = 'white', font="Lane",) 
	txt_clip = txt_clip.set_pos((200,613)).set_duration(duration) 
	temp = CompositeVideoClip([bg,txt_clip])
	return temp

def doTTS(source, types):
	file = './config/'+types+".wav"
	speech_config = SpeechConfig(subscription="YOUR-AZURE-API", region="eastus", speech_recognition_language='id-ID-ArdiNeural')
	speech_config.speech_synthesis_voice_name = 'id-ID-ArdiNeural'
	audio_config = AudioOutputConfig(filename=file)
	synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
	synthesizer.speak_text_async(source)

def doResize(image, dur):
	images = image
	size = (1280, 720)
	if ".mp4" in image:
		slide = VideoFileClip(image).set_duration(dur).resize(size)
		slide.audio = None
	else:
		try:
			slide = ImageClip(image).set_fps(30).set_duration(dur).resize(size)
		except Exception as e:
			print(str(e))
			exit()
			print(images)

		slide = slide.resize(lambda t: 1 + 0.04 * t)  # Zoom-in effect
		slide = slide.set_position(('center', 'center'))
	return slide

def getAudioLenght(source):
	voice = WAVE(source)
	dur = voice.info.length
	return dur

def Cleaning(source):
	source = source.replace('Covid','kovid')
	source = source.replace('covid','kovid')
	source = source.replace('COVID','kovid')
	source = source.replace('corona','korona')
	source = source.replace('Corona','korona')
	source = source.replace('(','atau ')
	source = source.replace(')','')
	source = source.replace('tahu','tau')
	source = source.replace('"','')
	source = source.replace('AS','Amerika Serikat')
	source = source.replace('USA','Amerika Serikat')
	source = source.replace('Sunscreen','sanskrin')
	source = source.replace(' loh','')
	source = source.replace('Affection','afeksien')
	source = source.replace('K-drama', 'Drama Korea')
	return source

def WorkBitch():
	final_clip = []
	temp_clip = []


	opening,transition = Assets()
	final_clip.append(opening)


	temp = open('config.json').read()
	config = json.loads(temp)
	print('[+] Config loaded')
	file_validate = CheckFile()
	if file_validate == True:
		print('[?] Please fix your image on config')
		exit()
	print('[+] Creating intro . . .', end=' ', flush=True)
	read_file = open('./config/'+config['file'], encoding='UTF8').read()
	#tts_intro = doTTS(read_file,config['file'])
	tts_lenght = getAudioLenght('./config/'+config['file']+".wav")
	duration = tts_lenght/len(config['image'])
	for i in config['image']:
		file = './config/image/'+i
		clip_temp = doResize(file,duration)
		temp_clip.append(clip_temp)
	intro_overlay = addoverlay(config['title'], tts_lenght)
	final = concatenate_videoclips(temp_clip, method='compose')
	finals = CompositeVideoClip([final,intro_overlay], size=(1280,720))
	audio = AudioFileClip('./config/'+config['file']+".wav")
	finals = finals.set_audio(audio)
	final_clip.append(finals)
	final_clip.append(transition)
	print('Done!')
	print('[+] Processing Section . . .')
	## Section Part
	for index in config['section']:
		temp_clip = []
		name = index['name']
		print('[+]', name, end=' ', flush=True)
		file = './config/'+index['file']
		read_tts = open('./config/'+index['file']).read()
		read_tts = Cleaning(read_tts)
		#doTTS(read_tts,index['file'])
		tts_lenght = getAudioLenght(file+".wav")
		duration = tts_lenght/len(index['image'])
		for i in range(len(index['image'])):
			image = './config/image/'+index['image'][i]
			temp_clip.append(doResize(image,duration))
		intro_overlay = addoverlay(name, tts_lenght)
		merge_temp = concatenate_videoclips(temp_clip, method="compose")
		result_temp = CompositeVideoClip([merge_temp, intro_overlay])
		audio = AudioFileClip(file+".wav")
		result_temp = result_temp.set_audio(CompositeAudioClip([audio]))
		final_clip.append(result_temp)
		final_clip.append(transition)
		print('Done!')

	all_final = concatenate_videoclips(final_clip, method="compose")
	bg_sound = BackSound(all_final.duration)
	audio_temp = CompositeAudioClip([bg_sound,all_final.audio])
	all_final.audio = audio_temp
	all_final = all_final.resize((1280,720))
	all_final.write_videofile(config['title']+".mp4", threads = 16, bitrate="5000k")


WorkBitch()