from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uvicorn
import cv2
import os
import uuid

UPLOAD_FOLDER = '/home/joyce/Pictures'
PROCESSED_FOLDER = '/home/joyce/Downloads'

app = FastAPI()

def process_image(path: str, destination_filename: str):
    image = cv2.imread(path)
    rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    destination_path = os.path.join(PROCESSED_FOLDER, destination_filename)
    cv2.imwrite(destination_path, rotated_image)

@app.post("/upload")
async def upload_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PNG or JPG image.")

    if file.filename == '':
        raise HTTPException(status_code=400, detail="Empty fileName.")

    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as image_file:
        content = await file.read()
        image_file.write(content)
    
    destination_filename = f"{uuid.uuid4()}.png"
    
    background_tasks.add_task(process_image, path, destination_filename)
  
    return {"message": "Image uploaded successfully", "download_url": f"/download/{destination_filename}"}

@app.get("/download/processed/{filename}")
def download_processed_image(filename: str):
    processed_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(processed_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(processed_path)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
