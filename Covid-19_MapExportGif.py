import geopandas
import geoplot
import pandas
import mapclassify
from geopandas import GeoDataFrame
import matplotlib
import matplotlib.pyplot as plt


#Get up-to-date Covid19 cases from CSSEGIS on Github

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
data_covid = pandas.read_csv(url, index_col=0)
data_covid = data_covid.drop(columns=['Lat', 'Long'])

#rename'Country/Region' value 'West Bank and Gaza' to 'Israel', so we can merge with already existing 'Israel'. 
#This is necessary as shape file doesn't list 'West Bank and Gaza'.
data_covid['Country/Region'] = data_covid['Country/Region'].replace({'West Bank and Gaza': 'Israel'})

#Aggregates numbers for countries that are divided into regions/states, such as Canada, China, US (or as manually created 'Israel')
dc_agg = data_covid.groupby(['Country/Region'], as_index = False).sum(axis=0, skipna=True).reset_index()

#Rename country column header to match lookup table that we maybe use later
dc_agg = dc_agg.rename(columns={'Country/Region' : 'Country_Region'})

#Gets rid of the unique locations not mapped out 
dc_agg = dc_agg[(dc_agg.Country_Region != 'Diamond Princess') & (dc_agg.Country_Region != 'MS Zaandam') & (dc_agg.Country_Region != 'Antarctica')]

#Renames countries according to shapefile:
dc_agg["Country_Region"] = dc_agg["Country_Region"].replace({"Bahamas":"The Bahamas","Burma" :"Myanmar","Congo (Brazzaville)" : "Republic of the Congo", "Congo (Kinshasa)" : "Democratic Republic of the Congo", "Cote d'Ivoire" : "Ivory Coast", "Holy See": "Vatican", "Korea, South": "South Korea", "North Macedonia": "Macedonia","Serbia":"Republic of Serbia", "Tanzania" : "United Republic of Tanzania", "Timor-Leste" : "East Timor", "US": "United States of America", "Taiwan*" : "Taiwan", "Eswatini":"eSwatini"})


#Load polygon shapefile of the world from https://www.naturalearthdata.com/
fp_sov = r'~\some_dir\ne_50m_admin_0_sovereignty.shp'
world = geopandas.read_file(fp_sov)

#Control export without 'geometry' as it wouldn't export otherwise
#world_csv = world.drop(columns='geometry').reset_index()
#world_csv.to_csv(r'~\some_dir\world_csv2.csv', index = False, header=True)

#We only need two columns, 'SOVEREIGNT' and 'geometry'
world_short = world.filter(items=['SOVEREIGNT', 'geometry'])

#Rename column 'SOVEREIGNT' to 'Country_Region', in order to match with data-dataframe
world_short = world_short.rename(columns={'SOVEREIGNT' : 'Country_Region'})


#merge data ('dc_agg') on shapefile ('world_short'), so that new file retains geodataframe format and right merge to retain datapoints 
covid_world = world_short.merge(dc_agg, on='Country_Region', how='outer') 

#Overriding NaN values with zero and 9999 where index column, respectively 
covid_world[covid_world.columns[3:]] = covid_world[covid_world.columns[3:]].fillna(0)
covid_world['index'] = covid_world['index'].fillna(9999)

#determine max data value for scaling and legend (selecting last column of data frame)
covid_max = covid_world.iloc[:,-1].max()

#Reconvert covid_world to geodataframe (to avoid exception being raised, not sure this is a fix though)
covid_world = geopandas.GeoDataFrame(
    covid_world, geometry=covid_world['geometry'])
    
# Ask for directory in which to store the png files created  
dir_name = input('Please provide the full path of the desired png directory: ') 

#Loop that gets colum indexes from index 3 (first data column) to index -1 (last column) and writes value to var 'index', then creates png per data column

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
    
    ax.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
    ax.text(0.88, 0.93, str(data_col_header), color='blue', 
         alpha=0.7, fontsize=40, transform = ax.transAxes)
    ax.text(0.55, 0.01, 'Data sources aggregated by JHU CSSE @ https://github.com/CSSEGISandData/COVID-19', color='#004C74', 
        alpha=1, fontsize=14, transform = ax.transAxes)
    
    #Customized data bins
    scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, 5000, 50000, 100000, covid_max])
        
    geoplot.choropleth(
      covid_world, hue=data_col, scheme=scheme, legend=True, legend_kwargs={'loc':'lower left', 'fontsize':16}, 
      cmap=cmap, norm=norm, ax=ax, extent=(-180, -60, 180, 90), 
    )

    fig1 = plt.gcf()

    # Reformat column header for filenames 
    from datetime import datetime
    data_col_header_formatted = datetime.strptime(str(data_col_header), '%m/%d/%y').date()
    
    # Create dir for png files 
    import os        
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ")

    filename = ('CovidByCountry_'+str(data_col_header_formatted)+'.png')
    fig1.savefig(dir_name + '/' + filename, bbox_inches='tight', pad_inches=0.1)

    plt.close('all')
    
    
#Get the number of (png) files in dir to establish duration sequences of gif
file_number = len([name for name in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, name))])

#Create list for gif sequence length
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

#Specify filename without file type
gif_fn = 'CovidByCountry'

fp_in = dir_name + '/CovidByCountry_2020*.png'
fp_out = dir_name + '/' + str(gif_fn) + '.gif'

img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
img.save(fp=fp_out, format='GIF', append_images=imgs,
         save_all=True, duration=list, loop=1)
