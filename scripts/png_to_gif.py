import os

import get_dir
from get_dir import dir_name
from get_dir import name_image


#Create list for length of sequences of gif
file_number = len([name for name in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, name))])
list = []
x =200
cycles = 0
cycles_max = file_number

while cycles < cycles_max-1:
    x = x+(x*0.018)
    list += [x]
    cycles = len(list)
list += [2000]

#Create GIF from png files
import imageio
import glob
from PIL import Image

#File(s) in/out
fp_in = dir_name + '/' + name_image + '2020-*.png'
fp_out = dir_name + '/' + name_image + '.gif'

img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
img.save(fp=fp_out, format='GIF', append_images=imgs,
         save_all=True, duration=list, loop=1, optimize=True, dpi=50)

