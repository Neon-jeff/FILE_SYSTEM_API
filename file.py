from fastapi import FastAPI,UploadFile,File,HTTPException,Response
from fastapi.responses import FileResponse
from pathlib import Path
import shutil,os
from schemas import FileUploadSchema
import random
import speech_recognition as sr
from pydub import AudioSegment
import whisper
import zipfile
import io

# Whisper configs
option=whisper.DecodingOptions(language='en',fp16=False)
model=whisper.load_model('tiny.en')



app=FastAPI()

# Helper function
def find_file(name,user):
    cwd=str(Path.cwd())
    file_path=f"{cwd}/videos/{user}"
    trans_path=f"{cwd}/transcriptions/{user}"
    file_list=os.listdir(file_path)
    t_list=os.listdir(trans_path)

    video_file,transcript=None,None
    for i in file_list:
        if i.split('.')[0] == name:
            video_file=i
            break
    for i in t_list:
        if i.split('.')[0] == name:
            transcript_file=i
            break
    return [video_file,transcript_file]

# Helper function

# def transcribe_video(file_path):
#     video = AudioSegment.from_file(file_path, format="mp4")
#     audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)
#     audio.export("audio.wav", format="wav")
#     r = sr.Recognizer()

# # Open the audio file
#     with sr.AudioFile("audio.wav") as source:
#         audio_text = r.record(source)
# # Recognize the speech in the audio
#     text = r.recognize_google(audio_text, language='en-US')
#     print(text)
#     return text

# try whisper configs


@app.get('',status_code=200)
def check_health():
    return {"health status":"ok"}


# @app.post('/add-user',summary="Adds a user directory to the file system or disk before they can use the API")
# def add_user():
#     pass

@app.get('/file/{user}',summary="Get all videos for a user")
def get_user_videos(user:str):
    cwd=str(Path.cwd())
    file_path=f"{cwd}/videos/{user}"
    transcription_path=f"{cwd}/transcriptions/{user}"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail={
                "message":"User not found"
            }
        )
    return {"user":user,"user_videos":os.listdir(file_path)}

@app.get('/file/{user}/{video_id}',summary="downloads a zip file of a user video and the transcription file")
def download_video(video_id:str,user:str):
    files=find_file(video_id,user)
    video,trans=files[0],files[1]
    cwd=str(Path.cwd())
    video_path=f"{cwd}/videos/{user}/{video}"
    t_path=f"{cwd}/transcriptions/{user}/{trans}"

    # zip file creation
    z_name="video.zip"
    s=io.BytesIO()
    zf=zipfile.ZipFile(s,'w')
    zf.write(video_path,video)
    zf.write(t_path,trans)
    zf.close()
    if video is not None:
        return Response(s.getvalue(), media_type="application/x-zip-compressed", headers={
        'Content-Disposition': f'attachment;filename={z_name}'
    })
    else:
        raise HTTPException(status_code=404,detail={
            "message":"File does not exist or User not found"
        })


@app.post('/file',summary="uploads video for a user, creates a video id and creates a folder or directory for the user, and also generates a transcript txt file")
async def upload_video(user:str,video:UploadFile=File(...)):
    # create a session a session id ?
    # create a path to store the videoes in the server
    path = Path.cwd()/'videos'/user
    trans_path = Path.cwd()/'transcriptions'/user

    try:
        path.mkdir(parents=True, exist_ok=False)
        trans_path.mkdir(parents=True,exist_ok=False)
    except FileExistsError:
        pass
    else:
        pass

    video_id=str(random.randint(0,10000))
    video.filename=video_id+'.mp4'
    video_trans=video_id+'.txt'
    file_path=f"{path}/{video.filename}"
    trans_name=f"{trans_path}/{video_trans}"
    # save video to memory
    with open(file_path,"wb") as f:
        shutil.copyfileobj(video.file,f)

    transcription=model.transcribe(file_path)
    # save transcription to memory
    with open(trans_name,'w') as f:
        f.write(transcription['text'])
    return {"uploaded":True,"file_path":file_path,"video_id":video_id,"transcription":transcription['text']}

