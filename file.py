from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil,os
from schemas import FileUploadSchema


app=FastAPI()

# Helper function
def find_file(name,user):
    cwd=str(Path.cwd())
    file_path=f"{cwd}/videos/{user}"
    file_list=os.listdir(file_path)
    file=None
    for i in file_list:
        if i.split('.')[0] == name:
            file=i
            break
    return file


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
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail={
                "message":"User not found"
            }
        )
    return {"user":user,"user_videos":os.listdir(file_path)}

@app.get('/file/{user}/{filename}',summary="downloads a stored user video")
def download_video(filename:str,user:str):

    file=find_file(name)
    cwd=str(Path.cwd())
    file_path=f"{cwd}/videos/{file}"

    if file is not None:
        return FileResponse(path=file_path,media_type='application/octet-stream',filename=file)
    else:
        raise HTTPException(status_code=404,detail={
            "message":"File does not exist or User not found"
        })


@app.post('/file',summary="uploads video for a user and creates a special directory for the user")
async def upload_video(user:str,video:UploadFile=File(...)):
    video_ext=video.filename.split('.').pop()
    # create a path to store the videoes in the server
    path = Path.cwd()/'videos'/user
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass
    else:
        pass

    file_path=f"{path}/{video.filename}"
    with open(file_path,"wb") as f:
        shutil.copyfileobj(video.file,f)
    return {"Uploaded":True,"file_path":file_path}

