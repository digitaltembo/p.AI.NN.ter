import cv2
import numpy
from PIL import Image

def opencv2pil(cv_image):
  cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
  return Image.fromarray(cv_image)

def pil2opencv(pil_image: Image.Image):
  return cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
