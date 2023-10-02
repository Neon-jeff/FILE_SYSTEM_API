from pydantic import BaseModel


class FileUploadSchema(BaseModel):
    user:str

