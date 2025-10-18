from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).parent
PUBLIC_DIR = BASE_DIR / "public"
CSV_FILE = BASE_DIR / "linkedin_internships_all_pages.csv"
HTML_FILE = BASE_DIR / "index.html"

@app.get("/csv")
def get_csv():
  # prefer CSV inside public if present
  public_csv = PUBLIC_DIR / "linkedin_internships_all_pages.csv"
  target = public_csv if public_csv.exists() else CSV_FILE
  if target.exists():
    return FileResponse(target)
  return {"message": "CSV file not found"}

if PUBLIC_DIR.exists():
  app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="public")
else:
  @app.get("/")
  def read_index():
    if HTML_FILE.exists():
      return HTMLResponse(content=HTML_FILE.read_text(encoding="utf-8"), status_code=200)
    return {"message": "index.html not found"}
