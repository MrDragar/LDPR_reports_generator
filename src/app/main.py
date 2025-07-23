import os
import uuid

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # Add this import

from app.pdf_creater import generate_pdf_report
from app.model import LDPRReport


app = FastAPI()
app.mount("/media", StaticFiles(directory="media"), name="media")
# Add these CORS middleware settings
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://192.168.43.199:80"],  # List of allowed origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники временно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Добавьте эту строку
)

@app.get("/ping")
async def ping():
    return {"message": "Pong"}


@app.post("/")
async def create_pdf(report: LDPRReport, request: Request):
    report_filename = f"report_{uuid.uuid4()}.pdf"
    report_filepath = os.path.join("media", report_filename)
    generate_pdf_report(report.dict(), report_filepath)
    return {"status": "Success", "message": f"{request.base_url}media/{report_filename}"}
