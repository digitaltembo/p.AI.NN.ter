import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from transforms import gfpgan, real_ersgan,stable_diffusion
from utils.file_utils import UPLOAD_DIR, OUTPUT_DIR, ROOT_DIR
from web import file_mgmt

app = FastAPI()

API_PATH = "/api"

app.include_router(gfpgan.router, prefix= API_PATH)
app.include_router(real_ersgan.router, prefix= API_PATH)
app.include_router(stable_diffusion.router, prefix= API_PATH)
app.include_router(file_mgmt.router, prefix= API_PATH)

app.mount('/uploads', StaticFiles(directory=UPLOAD_DIR))
app.mount('/output', StaticFiles(directory=OUTPUT_DIR))

REACT_FRONTEND_BUILD_DIR = os.path.join(ROOT_DIR, "src/web/frontend/build")
app.mount("/", StaticFiles(directory=REACT_FRONTEND_BUILD_DIR, html=True))