#Old imports, kept here just in case.
#   import json, os
#   import utilsCOCO
#   from PIL import Image, ImageDraw
#   from echo1_coco_split import *  #echo1_coco_split.main({'.\All-Dataset\\Android\\Annotations\\android_coco.json', 0.2, 0.1})

from LabelManager import LabelManager
from UtilLabelMe import UtilLabelMe

manager = LabelManager()
util = UtilLabelMe()
#Searching 'checkedtextview' label on all datasets
util.check_labels('checkedtextview')
#Opening "IMG_0754" image from "Iphone" dataset.
#util.image_processing('Iphone', 'IMG_0754')

