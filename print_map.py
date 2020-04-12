import geoplot.crs as gcrs
import geoplot
import mapclassify
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

import merge_data
from merge_data import covid_world
from merge_data import covid_max
import get_dir
from get_dir import col_val



###Plot per data column 
data_col = covid_world[str(col_val)]
data_col_header = (data_col.reset_index()).columns.values[1]
chart_date = datetime.strptime(str(data_col_header), '%m/%d/%y').strftime('%m/%d/%y')

norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

#Change projection to Miller in order to remove map distortions. For more classifiers check >> https://pysal.org/mapclassify/_modules/mapclassify/classifiers.html
import geoplot.crs as gcrs
ax = geoplot.polyplot(covid_world, gcrs.Miller(),figsize=(30, 15))
   
ax.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
ax.text(0.85, 0.93, str(chart_date), color='blue', 
    alpha=0.7, fontsize=40, transform = ax.transAxes)
ax.text(0.55, 0.01, 'Data sources aggregated by JHU CSSE @ https://github.com/CSSEGISandData/COVID-19', color='#004C74', 
    alpha=1, fontsize=14, transform = ax.transAxes)
    
#Customized data bins
scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, round(int(covid_max*0.01/1000)*1000), round(int(covid_max*0.1/10000)*1000), round(int(covid_max*0.5/10000)*1000), covid_max])
        
geoplot.choropleth(
    covid_world, hue=data_col, scheme=scheme, legend=True, legend_kwargs={'loc':'lower left', 'fontsize':16}, 
    cmap=cmap, norm=norm, ax=ax, extent=(-180, -60, 180, 90), 
)

fig1 = plt.gcf()

plt.show()
