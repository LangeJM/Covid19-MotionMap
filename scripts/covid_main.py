import covid_getdata

import worldall_getshape

import merge_data

import get_dir
from get_dir import out_option

if out_option != 'gif':
	import print_map
else:

	import draw_map
	import png_to_gif

