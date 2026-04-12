"""
AeroSight Business Reports API Endpoints
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from reports.generator import ReportGenerator
from backend.config import settings

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORTS_DIR = settings.reports_dir

@router.get("/list", summary="List Available Business Reports")
def list_reports():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        gen = ReportGenerator()
        gen.generate_all_reports()

    files = os.listdir(REPORTS_DIR)
    report_list = []
    for f in sorted(files):
        if f.endswith((".xlsx", ".csv", ".md", ".json")):
            f_path = os.path.join(REPORTS_DIR, f)
            size_kb = round(os.path.getsize(f_path) / 1024, 1)
            report_list.append({
                "filename": f,
                "file_type": "Excel Workbook" if f.endswith(".xlsx") else ("CSV Export" if f.endswith(".csv") else "Document"),
                "size_kb": size_kb,
                "download_url": f"/api/reports/download/{f}"
            })
    return report_list

@router.get("/download/{filename}", summary="Download Specific Business Report File")
def download_report(filename: str):
    # Sanitize filename
    safe_name = os.path.basename(filename)
    file_path = os.path.join(REPORTS_DIR, safe_name)
    
    if not os.path.exists(file_path):
        # Auto-generate if missing
        gen = ReportGenerator()
        gen.generate_all_reports()
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Report file not found")

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if safe_name.endswith(".xlsx") else "text/csv"
    return FileResponse(path=file_path, filename=safe_name, media_type=media_type)
