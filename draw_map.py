import geoplot.crs as gcrs
import geoplot
import mapclassify
import matplotlib
import matplotlib.pyplot as plt

import merge_data
from merge_data import covid_world
from merge_data import covid_max
import get_dir
from get_dir import dir_name
from get_dir import name_image
from datetime import datetime



###Plot and save png per data column 

for index in range(3,covid_world.shape[1]):
	


	norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
	cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

	#Change projection to Miller in order to remove map distortions. For more classifiers check >> https://pysal.org/mapclassify/_modules/mapclassify/classifiers.html
	import geoplot.crs as gcrs
	ax = geoplot.polyplot(covid_world, gcrs.Miller(),figsize=(30, 15))

	#'last_col' was originally meant to define a range for legend and colors/hue. Let's leave it for now.
	last_col = covid_world.iloc[:,-1]

	#'data_col' is the respective date column selected. 'data_col_header' returns a title with the header of the selected 'data_col' as string
	data_col = covid_world.iloc[:,index]
	data_col_header = (data_col.reset_index()).columns.values[1]
	chart_date = datetime.strptime(str(data_col_header), '%m/%d/%y').strftime('%m/%d/%y')
	    
	ax.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
	ax.text(0.88, 0.93, str(chart_date), color='blue', 
	    alpha=0.7, fontsize=40, transform = ax.transAxes)
	ax.text(0.55, 0.01, 'Data sources aggregated by JHU CSSE @ https://github.com/CSSEGISandData/COVID-19', color='#004C74', 
	    alpha=1, fontsize=14, transform = ax.transAxes)
	    
	#Customized data bins
	scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, round(int(covid_max*0.01/1000)*1000), round(int(covid_max*0.1/10000)*10000), round(int(covid_max*0.5/10000)*10000), covid_max])
	        
	geoplot.choropleth(
	    covid_world, hue=data_col, scheme=scheme, legend=True, legend_kwargs={'loc':'lower left', 'fontsize':16}, 
	    cmap=cmap, norm=norm, ax=ax, extent=(-180, -60, 180, 90), 
	)

	fig1 = plt.gcf()


	###Store png per plot
	# Reformat column header for filenames 
	from datetime import datetime
	data_col_header_formatted = datetime.strptime(str(data_col_header), '%m/%d/%y').date()
	    
	# Create dir for png files 
	import os        
	if not os.path.exists(dir_name):
	    os.mkdir(dir_name)
	    print("Directory " , dir_name ,  " Created ")

###Change dpi to higher value for higher res (dpi*2 = size*4!!!). This currently gives ~1000 x 600, depends on local settings though.  
	filename = (name_image+str(data_col_header_formatted)+'.png')
	fig1.savefig(dir_name + '/' + filename, bbox_inches='tight', pad_inches=0.1, optimize = True, dpi=50)
	plt.close('all')