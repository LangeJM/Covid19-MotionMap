
import merge_data
from merge_data import covid_world


#Ask for user input to determine if to create gif or a sample geo chart print    
out_option = input('\n''Two options:''\n''1. Create gif file that includes all data columns >> type "gif" followed by "Enter"''\n''2. Show geo chart for one column >> type anything folowed by "Enter"''\n')


if out_option == 'gif':

	dir_name = input('Please insert the full path of the desired png directory and hit enter: ')
	name_image = input('Please insert a name for the image files and hit enter or only hit enter for a default name: ')

	if name_image == '':
		name_image = 'image'

else:
	for col in covid_world.columns: 
	    print(col)
	
	col_val = input('Please refer to the column header list above and type the column to be used for the chart''\n')


	
