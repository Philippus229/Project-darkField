from PIL import Image, ImageDraw
import math, os
import numpy as np
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

ML_WIDTH = 33.59788359788
mlwr2 = (int(ML_WIDTH+1),)*2
RATIO_WH = 1.154700538
MLA_IOR = 1.6
WH_RATIO = 2
NEAR = -0.5 #relative to
FAR = 1     #display height

ML_HEIGHT = ML_WIDTH*RATIO_WH

out_size = (2560, 1440)

def get_mask(size):
    mask_img = Image.new("L", size, 0)
    ImageDraw.Draw(mask_img).ellipse((0, 0, size[0], size[1]), fill=255)
    return mask_img

out_img = Image.new("RGB", out_size, (0,0,0))
d = askdirectory()
imgs = [Image.open(os.path.join(d,f)).convert("RGBA") for f in os.listdir(d)]
max_ratio = math.tan(math.asin(math.sin(math.atan(WH_RATIO/2))/1.6))
near_size = NEAR*imgs[0].size[1]*max_ratio
far_size = FAR*imgs[0].size[1]*max_ratio

mlw0 = ML_WIDTH*imgs[0].size[0]/out_size[0]
mlh0 = ML_HEIGHT*imgs[0].size[1]/out_size[1]

circle_mask = get_mask(mlwr2)
for i, img in enumerate(imgs): #back->front
    cur_size = far_size+(near_size-far_size)*i/(len(imgs)-1)
    acs = abs(cur_size)
    for ml_row in range(-int((out_size[1]/2)/(0.75*ML_HEIGHT)), int((out_size[1]/2)/(0.75*ML_HEIGHT))+1):
        for ml_col in range(-int((out_size[0]/2)/ML_WIDTH+(abs(ml_row)%2)), int((out_size[0]/2)/ML_WIDTH)+1):
            img2 = img.copy()
            ml_img = Image.new("RGBA", (int(acs+1), int(acs+1)), (0,0,0,0))
            in_center = img.size[0]/2+(ml_col+0.5*(abs(ml_row)%2))*mlw0, img.size[1]/2+ml_row*0.75*mlh0
            out_tl = out_size[0]/2+(ml_col-0.5*(1-(abs(ml_row)%2)))*ML_WIDTH, out_size[1]/2+ml_row*0.75*ML_HEIGHT-0.5*ML_WIDTH
            in_tl = (max(0,round(in_center[0]-acs/2)), max(0,round(in_center[1]-acs/2)))
            in_br = (min(img.size[0],round(in_center[0]+acs/2+1)), min(img.size[1],round(in_center[1]+acs/2+1)))
            ml_img.paste(img2.crop((in_tl[0],in_tl[1],in_br[0],in_br[1])), (max(0,-round(in_center[0]-acs/2)),max(0,-round(in_center[1]-acs/2))))
            alpha = Image.new("L", mlwr2, 0)
            alpha.paste(ml_img.split()[-1].resize(mlwr2).rotate(180*(cur_size<0)), mask=circle_mask)
            out_img.paste(ml_img.resize(mlwr2).rotate(180*(cur_size<0)), (round(out_tl[0]),round(out_tl[1])), mask=alpha)
out_img.save(asksaveasfilename(title="Save as...", filetypes=[("PNG Files","*.png")]),"PNG")
