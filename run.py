import textwrap, os, glob, os.path, shutil, sys, librosa, random, argparse, configparser
from configparser import ConfigParser
from os import walk
from ast import alias
from ctypes import alignment
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from datetime import datetime
from string import ascii_letters
from pathlib import Path
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    ImageClip,
    clips_array,
    vfx,
    AudioFileClip,
    concatenate_audioclips,
    AudioClip,
)


ROOT_path = os.path.dirname(os.path.realpath(__file__))
config_object = ConfigParser()
config_object.read(os.path.join(ROOT_path, "config.ini"))

# FOLDERCONFIG
FOLDERCONFIG = config_object["FOLDERCONFIG"]
SOURCE_path = os.path.join(ROOT_path, FOLDERCONFIG["SOURCE_path"])
EXPORT_path = os.path.join(ROOT_path, FOLDERCONFIG["EXPORT_path"])
ASSETS_path = os.path.join(ROOT_path, FOLDERCONFIG["ASSETS_path"])
PASTPROJECTS_path = os.path.join(ROOT_path, FOLDERCONFIG["PASTPROJECTS_path"])
VOC_path = os.path.join(ROOT_path, FOLDERCONFIG["VOC_path"])

# HARDCODED ASSETS SUBPATH
AUDIO_path = os.path.join(ASSETS_path, "AUDIO")
FONTS_path = os.path.join(ASSETS_path, "FONTS")
FOOTAGE_path = os.path.join(ASSETS_path, "FOOTAGE")
TEMP_path = os.path.join(ASSETS_path, "TEMP")
VO_path = os.path.join(ASSETS_path, "VO")

# DESCRIPTION CONFIG
DESCRIPTIONCONFIG = config_object["DESCRIPTIONCONFIG"]
BEFORE_PROMPT = DESCRIPTIONCONFIG["BEFORE_PROMPT"]
AFTER_PROMPT = DESCRIPTIONCONFIG["AFTER_PROMPT"]
BEFORE_SHORTDESCRIPTION = DESCRIPTIONCONFIG["BEFORE_SHORTDESCRIPTION"]
AFTER_SHORTDESCRIPTION = DESCRIPTIONCONFIG["AFTER_SHORTDESCRIPTION"]

def scanDirFolders(path):
    list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]
    return list_subfolders_with_paths

def scanDirPNG(path):
    list_files_with_paths = [f.path for f in os.scandir(path) if f.is_file()]
    list_files_with_paths_png = []
    for file in list_files_with_paths:
        if file.endswith('.png'):
            list_files_with_paths_png.append(file)
    return list_files_with_paths_png

def getDateString():
    date_time = datetime.now()
    str_date_time = date_time.strftime("%Y%m%d-%H%M%S")
    return str_date_time

def cleanupFolder(path):
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))

def moveFolder(original, target):
    shutil.move(original, target)

def findTTIFile(PNGpath):
    fileName = os.path.basename(PNGpath)
    TTIfileName = fileName.replace('.png', '.TTI')
    TTI_path = PNGpath.replace('.png', '.TTI')
    for root, dirs, files in os.walk(VOC_path):
        if TTIfileName in files:
            shutil.copy(os.path.abspath(f'{root}\{TTIfileName}'), TTI_path)




    
# TESTPNG = r"D:\00 Working\PE BOT\00 SOURCE\reclaimed by nature by beeple  wallpaper  highly detailed  trending on artstation. [Stable Diffusion plms] 41338889.png"
# findTTIFile(TESTPNG)

# CLEAN UP TEMP FOLDER

if __name__ == '__main__':
        
    for folder in scanDirFolders(SOURCE_path):
        cleanupFolder(TEMP_path)
        
        CURRENTpngList = [] # Reset FOR EACH LOOP
        CURRENTpngList = scanDirPNG(folder)
        tempPNGpath = [] # Reset FOR EACH LOOP
        descriptionTXT = [] # Reset FOR EACH LOOP
        SHORTSList = [CURRENTpngList[n:n+30] for n in range(0, len(CURRENTpngList), 30)]
        
        
        for PNGpath in CURRENTpngList:
            
            # # TTI Info ----------------------------------------------------------------
            TTIpath = PNGpath.replace('.png', '.TTI')
            PNGname = os.path.basename(PNGpath)
            
            if os.path.exists(TTIpath) == False:
                findTTIFile(PNGpath)
                print("Downloading TTI from VOC Folder: " + PNGname)
            
            # else: 
            #     print("*      TTI File already existed: " + PNGname)
                
            TTIinfo = {}
            with open(TTIpath, 'r') as TTIfiles:
                for line in TTIfiles:
                    if "=" in line:
                        name, value = line.replace('\n', '').split('=')
                        TTIinfo[name] = value
                                
            # TTI VAR
            imgScript = TTIinfo["Script"]
            imgSeed = TTIinfo["Random seed"]
            imgSDscale = TTIinfo["Scale"]
            imgSDres = TTIinfo["Custom Resolution"]
            
            # Info Filter
            imgScript = imgScript.replace(' *', '')
            imgSDres = imgSDres.replace("16:9", "").replace("21:9", "").replace("9:16", "").replace("9:21", "").replace("360p", "").replace("480p", "").replace("720p", "").replace("1080p", "").replace(" ", "")
            
            
            # Info - Display Var 
            imgCaption = TTIinfo["Input Phrase"]
            imgLowerCaption = str(f'{imgScript}    |    Scale: {imgSDscale}    |    {imgSDres}')
            
            # ----------------------------------------------------------------

            # Enlarge Img # Img1 = Blur
            basewidth1 = 1920
            img1 = Image.open(PNGpath)
            wpercent1 = (basewidth1/float(img1.size[0]))
            hsize1 = int((float(img1.size[1])*float(wpercent1)))
            img1 = img1.resize((basewidth1,hsize1), Image.ANTIALIAS)
            img1 = img1.filter(ImageFilter.GaussianBlur(10))
            
            
            basewidth = 2160
            img2 = Image.open(PNGpath)
            wpercent = (basewidth/float(img2.size[1]))
            hsize = int((float(img2.size[0])*float(wpercent)))
            img2 = img2.resize((hsize,basewidth), Image.ANTIALIAS)


            # Add text 
            MAX_W, MAX_H = 1920, 2160
            hOffset = 0.98
            
            imDescription = Image.new('RGBA', (MAX_W, MAX_H), (0, 0, 0, 0))
            font = ImageFont.truetype("font/Stapel-Light.ttf", 48)
            font2 = ImageFont.truetype("font/Stapel-Medium.ttf", 48)


            avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
            max_char_count = int(imDescription.size[0] * 0.69 / avg_char_width)
            text = textwrap.fill(text=imgCaption, width=max_char_count)
            ImageDraw.Draw(imDescription).fontmode = "1"
            ImageDraw.Draw(imDescription).text(xy=(imDescription.size[0]/2, imDescription.size[1] / 2 * hOffset), text=text, spacing=15, align='center', font=font, fill='#FFFFFF', anchor='mm')
            ImageDraw.Draw(imDescription).text(xy=(imDescription.size[0]/2, imDescription.size[1]*0.94), text=imgLowerCaption, spacing=15, align='center', font=font2, fill='#FFFFFF', anchor='mm')

            # Combine
            background = Image.new("RGB", (3840, 2160), (0, 0, 0))
            background.paste(img1, (0,0))
            
            background.paste(img2, (int((1920-hsize)/2),0))
            background.paste(imDescription, (1920,0))
            
            # Export
            print("*      Processing: " + PNGname)
            
            isExist = os.path.exists(TEMP_path)
            if not isExist:
                os.makedirs(TEMP_path)
            
            
            backgroundRe = background.resize((1920, 1080), Image.Resampling.LANCZOS)
            backgroundRe.save(f'{TEMP_path}/{PNGname}', quality=100)
            tempPNGpath.append(f'{TEMP_path}/{PNGname}')
            
            # Description
            descriptionTXT.append(imgCaption)
            
        
        print("Creating Video using MoviePy...")
        clips = [ImageClip(m).set_duration(2)
        for m in tempPNGpath]

        # main_clip = concatenate_videoclips(clips, method="chain")
        # main_clip.write_videofile(EXPORT_path + f"/{getDateString()}-[{os.path.basename(folder)}].mp4", threads=24, bitrate="2000k", audio_codec="aac", fps=30, codec="h264_nvenc", remove_temp=True,) 

        main_clip = concatenate_videoclips(clips, method="chain")
        # overlay_clip = VideoFileClip(os.path.join(FOOTAGE_path, "4sbar1920.mov"))    #20221003
        # overlay_clip = vfx.loop(overlay_clip, duration=main_clip.duration)    #20221003
        
        
        # AUDIO COMPARTMENT
        audio_fileList = []
        audio_durationList = []
        audio_file_dict = {}
        pickedTrackList = []
        audios = []

        ## creating a list from music folder
        for audio_file in os.listdir(AUDIO_path):
            if audio_file.endswith('.wav'):
                audio_duration = librosa.get_duration(filename=os.path.join(AUDIO_path, audio_file))
                audio_fileList.append(audio_file)
                audio_durationList.append(audio_duration)
            

        for key, value in zip(audio_fileList, audio_durationList):
            audio_file_dict[key] = value
            
        # pick one track randomly
        pickedTrack = random.choice(list(audio_file_dict))
        pickedTracksDuration = audio_file_dict[pickedTrack]

        # # Display info: duration of picked track audio_file_dict[pickedTrack]
        print("*      Picked Track: " + pickedTrack + " | Duration: " + str(pickedTracksDuration))

        # Compare vid duration to track
        main_clipDuration = main_clip.duration
        pickedTrackList.append(pickedTrack)

        # run a loop to increase audio duration
        for x in range(0,50):
            if pickedTracksDuration <= main_clipDuration:
                OneMoreTrack = random.choice(list(filter(lambda ele: ele != pickedTrack, audio_file_dict)))
                pickedTrackList.append(OneMoreTrack)
                pickedTracksDuration = pickedTracksDuration + audio_file_dict[OneMoreTrack]
                
        for audio in pickedTrackList:
            numberOfTracks = len(pickedTrackList)
            audios.append(AudioFileClip(os.path.join(AUDIO_path, audio)))

        audioClips = concatenate_audioclips([audio for audio in audios])
        audioClips = audioClips.set_duration(main_clipDuration)


        
        # Remove dup from description list
        descriptionTXT_clean = [*set(descriptionTXT)]
        descriptionTXT_clean.insert(0, BEFORE_PROMPT)
        descriptionTXT_clean.append("\n")
        descriptionTXT_clean.append(AFTER_PROMPT)
        
        fileOutputName = EXPORT_path + f"/{getDateString()}-[{os.path.basename(folder)}]-FULL"
        # f"/{getDateString()}-[{os.path.basename(folder)}]-SHORTS"
        
        f = open(fileOutputName + f".txt", "x")
        for item in descriptionTXT_clean:
            f.write("%s\n" % item)
        f.close()

        # final_video = mp.CompositeVideoClip([main_clip, overlay_clip.set_position((0,1080-8))])    #20221003
        final_video = mp.CompositeVideoClip([main_clip])
        final_video = final_video.set_audio(audioClips)
        final_video = final_video.fx(afx.volumex, 0.7)
        final_video = final_video.audio_fadein(1)
        final_video = final_video.audio_fadeout(10)


        final_video.write_videofile(fileOutputName + f".mp4", threads=24, bitrate="2000k", audio_codec="aac", fps=30, codec="h264_nvenc", remove_temp=True,) 
        
        cleanupFolder(TEMP_path)
        
        
        
        emotionPrompt = "[excited] [excited] "
        voiceOverScript = emotionPrompt + "This is made by A I."
        
        
        for lists in SHORTSList:
            cleanupFolder(TEMP_path)
            
            if len(lists) >= 30:
                random.shuffle(lists)
                
                # MAKEING COVER
                cover = Image.new("RGB", (1080, 1920), (0, 0, 0))
                MAX_W, MAX_H = 1080, 1920
                fontsize = 160
                coverLoopCount = 0
                coverVHeight = 0
                coverBasewidth = 216
                
                for image in lists:
                    print("Processing Cover: " + image)
            
                    if (coverLoopCount == 5):
                        coverVHeight = coverVHeight + hsize1
                        coverLoopCount = 0
                        # vFactor = vFactor + 1
                    
                    img1 = Image.open(image)
                    wpercent1 = (coverBasewidth/float(img1.size[0]))
                    hsize1 = int((float(img1.size[1])*float(wpercent1)))
                    img1 = img1.resize((coverBasewidth,hsize1), Image.ANTIALIAS)
                    cover.paste(img1, (coverLoopCount * coverBasewidth, coverVHeight))
                                
                    coverLoopCount = coverLoopCount + 1
                    
                
                imDescription = Image.new('RGBA', (MAX_W, MAX_H), (0, 0, 0, 0))
                font = ImageFont.truetype(FONTS_path + "/Stapel-ExtraBold.ttf", fontsize)

                avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
                max_char_count = int(imDescription.size[0] * 1 / avg_char_width)
                text = textwrap.fill(text=voiceOverScript.replace(emotionPrompt, "").replace(".", "").replace(" A I", " AI").replace(" G T A", " GTA"), width=max_char_count)
                
                ImageDraw.Draw(imDescription).fontmode = "1"
                ImageDraw.Draw(imDescription).text(xy=(imDescription.size[0]/2, imDescription.size[1] / 2), text=text, spacing=10, align='center', font=font, fill='#FFFFFF', anchor='mm', stroke_width=6, stroke_fill='black')


                # Adding Black Transparent Background
                nlines = text.count('\n')
                nlines = nlines + 1
                blackBackground_height = nlines * fontsize
                blackBackground = Image.new('RGBA', (MAX_W, blackBackground_height), (0, 0, 0, 200))
                
                
                
                # PNG Overlay
                # gCoverpng = Image.open("assets/shorts-cover.png")
                # cover.paste(gCoverpng, (0, 0), gCoverpng)
                
                newCover = Image.new('RGB', (MAX_W, MAX_H), (0, 0, 0))
                
                newCover.paste(cover, (0, 0))
                # Composite Image
                newCover.paste(blackBackground, (0, (1920 - blackBackground_height) // 2), blackBackground)
                newCover.paste(imDescription, (0, (1920 - MAX_H) // 2 + 10), imDescription)
                

                # Saving Cover PNG
                newCover.save(f'{TEMP_path}/001 cover.png', quality=100)
                frameFolderFileList = []
                # frameFolderFileList.append(f'{TEMP_path}/001 cover.png')
                
                contentBasewidth = 960
                contentBasewidth2 = 1080
                content = Image.new('RGB', (MAX_W, MAX_H), (0, 0, 0))
                
                
                for image in lists:
                    shortsPNGname = os.path.basename(image)
                    print("Processing Content: " + shortsPNGname)
                    
                    contentimg1 = Image.open(image)
                    
                    wpercent1 = (contentBasewidth/float(contentimg1.size[0]))
                    hsize1 = int((float(contentimg1.size[1])*float(wpercent1)))
                    contentimg1 = contentimg1.resize((contentBasewidth,hsize1), Image.ANTIALIAS)


                    # Gaussian Blur Background
                    contentimg2 = Image.open(image)
                    
                    wpercent2 = (contentBasewidth2/float(contentimg2.size[0]))
                    hsize2 = int((float(contentimg2.size[1])*float(wpercent2)))
                    contentimg2 = contentimg2.resize((contentBasewidth2,hsize2), Image.ANTIALIAS)
                    contentimg2 = contentimg2.filter(ImageFilter.GaussianBlur(10))
                    
                    
                    content.paste(contentimg2, (0, 0))
                    content.paste(contentimg1, ((1080-contentimg1.size[0]) // 2, 0))
                    
                    content.save(os.path.join(TEMP_path, shortsPNGname), quality=100)
                    
                
                # random.shuffle(frameFolderFileList)         
                
                frameFolderFileList = scanDirPNG(TEMP_path)
                print(frameFolderFileList)
                
                imgSeqClips = [ImageClip(m).set_duration(1)
                for m in frameFolderFileList]    
                
                content_clip = concatenate_videoclips(imgSeqClips, method="chain")
                
                clipList = []
                
                # get wav length
                audio_duration = librosa.get_duration(filename=os.path.join(VO_path, "001-1.wav"))
                
                # image to moviepy seq using that length       
                clip = ImageClip(os.path.join(TEMP_path, "001 cover.png")) 
                audioClip = AudioFileClip(os.path.join(VO_path, "001-1.wav"))
                clip = clip.set_duration(audioClip.duration)
                clip = clip.set_audio(audioClip)
                
                clipList.append(clip)
                clipList.append(content_clip)
                finalClip = mp.concatenate_videoclips(clipList)
                
                
                # AUDIO COMPARTMENT
                audio_fileList = []
                audio_durationList = []
                audio_file_dict = {}
                pickedTrackList = []

                ## creating a list from music folder
                for audio_file in os.listdir(AUDIO_path):
                    if audio_file.endswith('.wav'):
                        audio_duration = librosa.get_duration(filename=os.path.join(AUDIO_path, audio_file))
                        audio_fileList.append(audio_file)
                        audio_durationList.append(audio_duration)
                    

                for key, value in zip(audio_fileList, audio_durationList):
                    audio_file_dict[key] = value
                    

                # pick one track randomly
                pickedTrack = random.choice(list(audio_file_dict))
                pickedTracksDuration = audio_file_dict[pickedTrack]

                # # Display info: duration of picked track audio_file_dict[pickedTrack]
                print("Picked Track: " + pickedTrack + " | Duration: " + str(pickedTracksDuration))


                # Compare vid duration to track
                main_clipDuration = finalClip.duration

                pickedTrackList.append(pickedTrack)

                # run a loop to increase audio duration
                for x in range(0,50):
                    if pickedTracksDuration <= main_clipDuration - 45:
                        # not enough audio length, picking one more
                        # OneMoreTrack = random.choice(list(audio_file_dict))
                        OneMoreTrack = random.choice(list(filter(lambda ele: ele != pickedTrack, audio_file_dict)))
                        
                        pickedTrackList.append(OneMoreTrack)
                        pickedTracksDuration = pickedTracksDuration + audio_file_dict[OneMoreTrack]
                        
                
                audios = []

                for audio in pickedTrackList:
                    numberOfTracks = len(pickedTrackList)
                    audios.append(AudioFileClip(os.path.join(AUDIO_path, audio)))


                audioClips = concatenate_audioclips([audio for audio in audios])
                
                
                # audioClips = audioClips.set_duration(main_clipDuration)
                
                

                newAudioClip = mp.CompositeAudioClip([audioClips.set_start(-45).volumex(0.5).audio_fadein(5), finalClip.audio.volumex(1.8)])
                # newAudioClip = audioClips.set_duration(main_clipDuration)
                
                # adjustedNewAudioClip = mp.CompositeAudioClip([newAudioClip, finalClip.audio])

                finalClip = finalClip.set_audio(newAudioClip)
                finalClip = finalClip.set_duration(main_clipDuration)
                
                
                finalClip = finalClip.fx(afx.volumex, 0.7)
                finalClip = finalClip.audio_fadein(1)
                finalClip = finalClip.audio_fadeout(1)
                        

                fileOutputName = EXPORT_path + f"/{getDateString()}-[{os.path.basename(folder)}]-SHORTS"
                finalClip.write_videofile(fileOutputName + f".mp4", threads=24, bitrate="2000k", audio_codec="aac", fps=30, codec="h264_nvenc", remove_temp=True,) 
    
    
        moveFolder(folder, PASTPROJECTS_path)
                        
                        
                
                
                
                
                





















