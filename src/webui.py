from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from transforms import gfpgan, real_ersgan,stable_diffusion
from utils.file_utils import UPLOAD_DIR, OUTPUT_DIR
from web import file_mgmt

app = FastAPI()

app.include_router(gfpgan.router)
app.include_router(real_ersgan.router)
app.include_router(stable_diffusion.router)
app.include_router(file_mgmt.router)
app.mount('/uploads', StaticFiles(directory=UPLOAD_DIR))
app.mount('/output', StaticFiles(directory=OUTPUT_DIR))