import os
import uuid

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.pdf_creater import generate_pdf_report
from app.model import LDPRReport


app = FastAPI()
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/ping")
async def ping():
    return {"message": "Pong"}


@app.post("/")
async def create_pdf(report: LDPRReport, request: Request):
    report_filename = f"report_{uuid.uuid4()}.pdf"
    report_filepath = os.path.join("media", report_filename)
    generate_pdf_report(report.dict(), report_filepath)
    return {"status": "Succes", "message": f"{request.base_url}media/{report_filename}"}
