"""
Create a geo map with world-wide cases of Covid19 based on up-to-date data from
data repository by Johns Hopkins CSSE and provide either
1. a print out for one specific date
2. a gif which includes all dates
3. a movie which includes all dates.
"""
import os
import datetime
from datetime import datetime
import glob
import requests

import pandas
import geopandas
import fiona
import geoplot
import geoplot.crs as gcrs
import mapclassify
import matplotlib
import matplotlib.pyplot as plt
#import imageio
from PIL import Image



def get_data():
    """Gets data of Covid19 cases world wide from data repository by Johns Hopkins CSSE
    @https://github.com/CSSEGISandData/COVID-19 by way of csv import. Performs some
    data cleaning to align with later used shape file."""
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    data_covid = pandas.read_csv(url, index_col=0)
    data_covid = data_covid.drop(columns=['Lat', 'Long'])

    #Shape file used later doesn't list 'West Bank and Gaza' separately but has it included
    #under 'Israel'. Also, shapefile doesn't distinguish regions within countries.
    data_covid['Country/Region'] = data_covid['Country/Region'].replace({'West Bank and Gaza'\
    	                                                               :'Israel'})
    data_covid = data_covid.groupby(['Country/Region'], as_index=False).sum(axis=0, skipna=True)

    #Rename country column header to match lookup table that we maybe use later.
    data_covid = data_covid.rename(columns={'Country/Region' : 'Country_Region'})

    #Delete historical/unique locations not mapped out.
    data_covid = data_covid[(data_covid.Country_Region != 'Diamond Princess')\
	                    & (data_covid.Country_Region != 'MS Zaandam')\
	                    & (data_covid.Country_Region != 'Antarctica')]

    #Rename countries in alignment with shapefile.
    data_covid["Country_Region"] = data_covid["Country_Region"].replace({"Bahamas":"The Bahamas",\
									     "Burma" :"Myanmar", "Congo (Brazzaville)" : "Republic of the Congo",\
									     "Congo (Kinshasa)" : "Democratic Republic of the Congo",\
									     "Cote d'Ivoire" : "Ivory Coast", "Holy See": "Vatican",\
									     "Korea, South": "South Korea", "North Macedonia": "Macedonia",\
									     "Serbia":"Republic of Serbia", "Tanzania" : "United Republic of Tanzania",\
									     "Timor-Leste" : "East Timor", "US": "United States of America",\
									     "Taiwan*" : "Taiwan", "Eswatini":"eSwatini"})

    return data_covid

get_data()



def get_shape_from_url():
    """Get the world shapefile to draw geo map within a zip file via url
    """
    print('\n''Link of zip file containing a world shape file: ''\n''https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip''\n')


    standard_url = 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'

    user_input = input('Please provide the full url to the zip file or hit any key to use the standard link provided above.')

    for _x in user_input:
        if not user_input.startswith('http'):
            url = standard_url
        else:
            url = user_input

    request = requests.get(url)
    _b = bytes(request.content)
    with fiona.BytesCollection(_b) as _f:
        crs = _f.crs
        world_all = geopandas.GeoDataFrame.from_features(_f, crs=crs)

    #We only need two columns, 'SOVEREIGNT' and 'geometry'
    world_all = world_all.filter(items=['ADMIN', 'geometry'])

    #Rename column 'SOVEREIGNT' to 'Country_Region', in order to align with data source
    world_all = world_all.rename(columns={'ADMIN' : 'Country_Region'})

    #Rename country to align with data source
    world_all['Country_Region'] = world_all['Country_Region'].replace({"SÃ£o TomÃ© and Principe"\
        :"Sao Tome and Principe"})

    return world_all

get_shape_from_url()


def get_shape_from_local():
    """Get the world shapefile to draw geo map from local path
    """
    local_path = input('Please provide the full local path and filename of the shape file, e.g. \
        C:/Users/lange/data/world.shp')
    world_all = geopandas.read_file(local_path)

    return world_all



def merge_data_shape():
    """Merge both data and shape file
    """
    covid_world = world_all.merge(data_covid, on='Country_Region', how='outer').reset_index()

    #Override NaN values with zero and 9999 where index column, respectively.
    covid_world[covid_world.columns[3:]] = covid_world[covid_world.columns[3:]].fillna(0)
    covid_world['index'] = covid_world['index'].fillna(9999)

    #Get overall max data value for scaling and map legend (selected as max value from last column)
    covid_max = covid_world.iloc[:, -1].max()

    #Reenforce geodataframe format (to avoid exception, seems this is not a solid fix though)
    covid_world = geopandas.GeoDataFrame(
        covid_world, geometry=covid_world['geometry'])

    return covid_world, covid_max

merge_data_shape()


def merged_to_csv():
    """Control export of shape file without 'geometry' as it wouldn't export otherwise
    """
    query_user_csv = input('If you want to export the merged file as csv and have a \
        look before we proceed, please type "Yes" or "Y", otherwise press any key.')
    if query_user_csv == 'Yes' | 'Y':
        covid_world_csv = covid_world.drop(columns='geometry').reset_index()
        covid_world_csv.to_csv('covid_world.csv', index=True, header=True)
        print('Press any key to continue.')

merged_to_csv()


def get_output_type():
    """Get path for save Ask for user input to determine if to create gif or a \
    sample geo chart print
    """
    col_val = None
    out_option = input('\n''Please choose from one of three output options:''\n'\
        '1. To create a gif file that includes all data, type "gif" followed by "Enter"''\n'\
        '2. Creation of a movie file is coming soon. Nothin to select yet :/..''\n'\
        '3. To merely show geo chart for one column >> type any key followed by "Enter"''\n')
        #'2. To create a movie file that includes all data, type "movie" followed by "Enter"''\n'\

    if out_option == 'gif':
        output = 'gif'

    elif out_option == 'movie':
        output = 'movie'

    else:
        for col in covid_world.columns:
            print(col)

        col_val = input('Please refer to the column header list above and type the column \
            to be used for the chart''\n')

    if out_option == 'gif' | 'movie':

        dir_name = input('Please insert the full path of the desired png directory and hit enter: ')

        name_image = input('Please insert a name for the image files and hit enter or only \
            hit enter for a default name: ')

        if name_image == '':
            name_image = 'image'

    return output, col_val, name_image, dir_name

get_output_type()

def show_map():
    """Display geo map for user-specified date
    """
    data_col = covid_world[str(col_val)]
    data_col_header = (data_col.reset_index()).columns.values[1]
    chart_date = datetime.strptime(str(data_col_header), '%m/%d/%y').strftime('%m/%d/%y')

    norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
    cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

    #Change projection to Miller in order to remove map distortions. \
    #Check alt classifiers >> https://pysal.org/mapclassify/_modules/mapclassify/classifiers.html
    ax1 = geoplot.polyplot(covid_world, gcrs.Miller(), figsize=(30, 15))
    ax1.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
    ax1.text(0.85, 0.93, str(chart_date), color='blue', alpha=0.7, fontsize=40, \
        transform=ax1.transAxes)
    ax1.text(0.55, 0.01, \
            'Data sources aggregated by JHU CSSE @ https://github.com/CSSEGISandData/COVID-19', \
            color='#004C74', alpha=1, fontsize=14, transform=ax1.transAxes)

    #Customized data bins.
    scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, round(int(covid_max*0.01/1000)\
        *1000), round(int(covid_max*0.1/10000)*1000), round(int(covid_max*0.5/10000)*1000), \
    covid_max])

    geoplot.choropleth(covid_world, hue=data_col, scheme=scheme, legend=True, \
        legend_kwargs={'loc':'lower left', 'fontsize':16}, cmap=cmap, norm=norm, ax=ax1, \
        extent=(-180, -60, 180, 90),)

    #fig1 = plt.gcf()

    plt.show()


def save_map_to_png():
    """Save geo maps as png files for every date in date row.
    """
    for index in range(3, covid_world.shape[1]):
    #Sequence that plots and saves png for every date in date row.
        norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
        cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

        #Change projection to Miller in order to remove map distortions. \
        #Chk alt classifiers >> https://pysal.org/mapclassify/_modules/mapclassify/classifiers.html
        ax1 = geoplot.polyplot(covid_world, gcrs.Miller(), figsize=(30, 15))

        #data_col is the respective date column selected.
        data_col = covid_world.iloc[:, index]
        #Convert to date to provide as secondary title.
        data_col_header = (data_col.reset_index()).columns.values[1]
        chart_date = datetime.strptime(str(data_col_header), '%m/%d/%y').strftime('%m/%d/%y')

        ax1.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
        ax1.text(0.88, 0.93, str(chart_date), color='blue', \
                alpha=0.7, fontsize=40, transform=ax1.transAxes)
        ax1.text(0.55, 0.01, \
                'Data sources aggregated by JHU CSSE @ https://github.com/CSSEGISandData/COVID-19', \
                color='#004C74', alpha=1, fontsize=14, transform=ax1.transAxes)

        #Customized data bins
        scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, \
            round(int(covid_max*0.01/1000)*1000), round(int(covid_max*0.1/10000)*10000), \
            round(int(covid_max*0.5/10000)*10000), covid_max])

        geoplot.choropleth(covid_world, hue=data_col, scheme=scheme, legend=True, \
            legend_kwargs={'loc':'lower left', 'fontsize':16}, cmap=cmap, norm=norm, ax=ax1, \
            extent=(-180, -60, 180, 90),)

        fig1 = plt.gcf()


        #Reformat column header for filenames.
        data_col_header_formatted = datetime.strptime(str(data_col_header), '%m/%d/%y').date()

        #Create dir for png files.
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            print("Directory ", dir_name, " Created ")

        #Change dpi to higher value for higher res (dpi*2 = size*4!!!). \
        #This currently gives ~1000 x 600, depends on local settings though.
        filename = (name_image + str(data_col_header_formatted) + '.png')
        fig1.savefig(dir_name + '/' + filename, bbox_inches='tight', pad_inches=0.1, \
            optimize=True, dpi=50)

        plt.close('all')

def png_to_gif():
    """Make gif file from png files created before.
    """
    #Create list for length of sequences of gif
    file_number = len([name for name in os.listdir(dir_name) \
        if os.path.isfile(os.path.join(dir_name, name))])
    list_dur = []
    dur = 200
    cycles = 0
    cycles_max = file_number

    while cycles < cycles_max-1:
        dur = dur + (dur*0.018)
        list_dur += [dur]
        cycles = len(list_dur)
    list_dur += [2000]

    #File(s) in/out
    fp_in = dir_name + '/' + name_image + '2020-*.png'
    fp_out = dir_name + '/' + name_image + '.gif'

    img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
    img.save(fp=fp_out, format='GIF', append_images=imgs, save_all=True, duration=list_dur, \
            loop=1, optimize=True, dpi=50)



# def png_to_movie
#     """Make gif file from png files created before.
#     Cominmg soon...
#     """
#     #Create list for length of sequences of gif
#     file_number = len([name for name in os.listdir(dir_name) \
#     if os.path.isfile(os.path.join(dir_name, name))])
#     list = []
#     x =200
#     cycles = 0
#     cycles_max = file_number

#     while cycles < cycles_max-1:
#         x = x+(x*0.018)
#         list += [x]
#         cycles = len(list)
#     list += [2000]

#     #File(s) in/out
#     fp_in = dir_name + '/' + name_image + '2020-*.png'
#     fp_out = dir_name + '/' + name_image + '.avi'


#     images = [img for img in os.listdir(fp_in) if img.endswith(".png")]
#     frame = cv2.imread(os.path.join(fp_in, images[0]))
#     height, width, layers = frame.shape

#     video = cv2.VideoWriter(fp_out, 0, 1, (width,height))

#     for image in images:
#         video.write(cv2.imread(os.path.join(fp_in, image)))

#     cv2.destroyAllWindows()
#     video.release()


def covid_output():
    """Based on user selection of ouput type, this function will show a greo map of
    the respective date picked by user or create a gif file from all png files created before.
    """
    if output == 'gif':
        save_map_to_png()
        png_to_gif()

    elif option == 'movie':
        save_map_to_png()
        #insert here fcuntion 'png_to_mp4' once done

    else:
        show_map()

covid_output()
