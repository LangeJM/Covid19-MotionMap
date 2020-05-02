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
import msvcrt
import tkinter as tk
from tkinter import filedialog
import requests

import pandas
import geopandas
import fiona
import geoplot
import geoplot.crs as gcrs
import mapclassify
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image


def get_and_process_data():
    """Gets data of Covid19 cases world wide from data repository by Johns Hopkins CSSE
    @https://github.com/CSSEGISandData/COVID-19 by way of csv import. Cleans data and merges with shape file to create geodataframe to be plotted."""

    ###Get coivid data

    data_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    data_covid = pandas.read_csv(data_url, index_col=0)
    data_covid = data_covid.drop(columns=['Lat', 'Long'])
    #Rename country column header to match lookup table that we maybe use later.
    data_covid = data_covid.rename(columns={'Country/Region' : 'Country_Region'})
    #Delete historical/unique locations not mapped out.
    data_covid = data_covid[(data_covid.Country_Region != 'Diamond Princess')\
	                    & (data_covid.Country_Region != 'MS Zaandam')\
	                    & (data_covid.Country_Region != 'Antarctica')]

    # Rename countries in alignment with shapefile. E.g. shape file used later doesn't list
    #"West Bank and Gaza" separately but has it included under "Israel". Also, shapefile
    #doesn't distinguish regions within countries.
    data_covid["Country_Region"] = data_covid["Country_Region"].replace({"West Bank and Gaza" \
                                         :"Israel", "Bahamas":"The Bahamas", "Burma" :"Myanmar", \
                                         "Congo (Brazzaville)" : "Republic of the Congo",\
									     "Congo (Kinshasa)" : "Democratic Republic of the Congo",\
									     "Cote d'Ivoire" : "Ivory Coast", "Holy See": "Vatican",\
									     "Korea, South": "South Korea", "North Macedonia": "Macedonia",\
									     "Serbia":"Republic of Serbia", "Tanzania" : "United Republic of Tanzania",\
									     "Timor-Leste" : "East Timor", "US": "United States of America",\
									     "Taiwan*" : "Taiwan", "Eswatini":"eSwatini"})

    #Consolidate countries (sum values and delete duplicates)
    data_covid = data_covid.groupby(['Country_Region'], as_index=False).sum(axis=0, skipna=True)

    ###Get the world shapefile to draw geo map within a zip file via url#

    #user input shape source
    standard_url = 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
    print('\n''Link of zip file containing a world shape file: ''\n' + str(standard_url) + '\n')
    print('Three options of shape file source: ''\n''1. Hit "Enter" to use the standard link provided above.''\n''2. Select the local path to the zip file' '\n')
    #Read keystroke without 'Enter'
    input_char = msvcrt.getch()
    shape_url = ''

    if input_char == b'1' or b'':
        #standard link/ url
        shape_url = standard_url
        print('' '\n' 'You chose option #1' '\n' 'Loading the shape file can take some time, depending on the connection to the source server.' '\n')

        #Convert shape to gdf
        request = requests.get(shape_url)
        _b = bytes(request.content)
        with fiona.BytesCollection(_b) as _f:
            crs = _f.crs
            world_all = geopandas.GeoDataFrame.from_features(_f, crs=crs)

    elif input_char == b'2':
        # Local zip file via file picker dialogue. To show only the dialog without any other GUI
        #elements, you have to hide the root window using the withdraw method.
        root = tk.Tk()
        root.withdraw()
        shape_url = filedialog.askopenfilename()
        #print(shape_url)
        shape_url = shape_url[3:]
        shape_url = 'zip:///' + shape_url
        #shape_url = str(shape_url)
        #print(shape_url)
        world_all = geopandas.read_file(shape_url)

        # _b = bytes(shape_url)
        # with fiona.BytesCollection(_b) as _f:
        #     crs = _f.crs
        #     world_all = geopandas.GeoDataFrame.from_features(_f, crs=crs)

        print('' '\n' 'You chose option #2' '\n')

    #We only need two columns, 'SOVEREIGNT' and 'geometry'
    world_all = world_all.filter(items=['ADMIN', 'geometry'])

    #Rename column 'SOVEREIGNT' to 'Country_Region', in order to align with data source
    world_all = world_all.rename(columns={'ADMIN' : 'Country_Region'})

    #Rename country to align with data source
    world_all['Country_Region'] = world_all['Country_Region'].replace({"SÃ£o TomÃ© and Principe"\
        :"Sao Tome and Principe"})


    ### Merge both data and shape file

    _covid_world = world_all.merge(data_covid, on='Country_Region', how='outer').\
    reset_index()

    #Override NaN values with zero and 9999 where index column, respectively.
    _covid_world[_covid_world.columns[3:]] = _covid_world[_covid_world.columns[3:]].fillna(0)
    _covid_world['index'] = _covid_world['index'].fillna(9999)

    #Get overall max data value for scaling and map legend (selected as max value from last column)
    _covid_max = _covid_world.iloc[:, -1].max()

    #Reenforce geodataframe format (to avoid exception, seems this is not a solid fix though)
    _covid_world = geopandas.GeoDataFrame(
        _covid_world, geometry=_covid_world['geometry'])

    #Last column for standard value of 'def show_map'
    _covid_last = _covid_world.iloc[:, -1]
    _covid_last = _covid_last.reset_index().columns.values[1]

    # User input of control export of shape file without 'geometry' as it wouldn't export otherwise
    print('Do you want to inspect the merged file as csv before we proceed [y/n]?''\n')
    input_csv = msvcrt.getch()

    if input_csv.lower() == b'y':
        input('A csv control file has been saved to your current directory. Press any key to continue.')
        covid_world_csv = _covid_world.drop(columns='geometry').reset_index()
        covid_world_csv.to_csv('covid_world.csv', index=True, header=True)
    elif input_csv.lower() == b'n':
        print('You chose not to save a csv control file.')

    print('')

    return _covid_max, _covid_world, _covid_last


def get_output_type():

    """Get path for save Ask for user input to determine if to create gif or a sample geo chart
    print.
    """
    _name_image = ''
    _dir_name = ''
    _col_val = None
    
    print('\n''Please choose from one of three output options:''\n' '1. Create a gif file that includes all data''\n' '2. Create a movie file that includes all data. Nothing to select yet, is coming soon. :/..''\n' '3. Show geo chart for pre-selected date. (This is the standard selection)''\n')
    print('')

    _out_option = msvcrt.getch()

    if _out_option == b'1':
        #_out_option == '1'
        print('Please select the directory to store the png files.''\n')
        root = tk.Tk()
        root.withdraw()
        _dir_name = filedialog.askdirectory()
        _name_image = input('Please type a name for the image files and hit "Enter". (Default name is "image")''\n')
        if _name_image == '':
            _name_image == 'image'

    elif _out_option == b'2':
        #_out_option == '2'
        print('This option is not available yet and I did not loop this, so, unfortunately, this selection ends the program.')
        input('Press "Enter" to exit.')


    elif _out_option is not (b'1' and b'2'):
        #_out_option == '3'
        print(COVID_WORLD.columns[3:])
        print('')

        _col_val = input('Please select a date from the list above to be used for the chart and confirm with "Enter".' '\n'\
            '(Standard selection is the most recent date)''\n')

        _col_val = _col_val.strip(chr(39))

        if _col_val in COVID_WORLD.columns[3:]:
            _col_val = str(_col_val)

        else:
            _col_val = str(COVID_LAST)

    print('')

    return _out_option, _col_val, _name_image, _dir_name


def show_map():
    """Display geo map for user-specified date
    """
    covid_max_int = int(COVID_MAX)

    data_col = COVID_WORLD[str(COL_VAL)]
    data_col_header = (data_col.reset_index()).columns.values[1]
    chart_date = datetime.strptime(str(data_col_header), '%m/%d/%y').strftime('%m/%d/%y')

    norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
    cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

    #Change projection to Miller in order to remove map distortions. \
    #Check alt classifiers >> https://pysal.org/mapclassify/_modules/mapclassify/classifiers.html
    ax1 = geoplot.polyplot(COVID_WORLD, gcrs.Miller(), figsize=(30, 15))
    ax1.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
    ax1.text(0.85, 0.93, str(chart_date), color='blue', alpha=0.7, fontsize=40, \
        transform=ax1.transAxes)
    ax1.text(0.55, 0.01, \
            'Data sources aggregated by JHU CSSE @ https://github.com/CSSEGISandData/COVID-19', \
            color='#004C74', alpha=1, fontsize=14, transform=ax1.transAxes)

    #Customized data bins.
    bin_4 = round(int(COVID_MAX*0.01/1000)*1000)
    bin_5 = round(int(COVID_MAX*0.1/10000)*10000)
    bin_6 = round(int(COVID_MAX*0.5/10000)*10000)
    scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, \
        round(int(COVID_MAX*0.01/1000)*1000), \
        round(int(COVID_MAX*0.1/10000)*10000), \
        round(int(COVID_MAX*0.5/10000)*10000), covid_max_int])

    geoplot.choropleth(COVID_WORLD, hue=data_col, scheme=scheme, legend=True, \
        legend_kwargs={'loc':'lower left', 'fontsize':16}, cmap=cmap, norm=norm, ax=ax1, \
        extent=(-180, -60, 180, 90), legend_labels=['0 - 10', '10 - 300', \
        '300 - 1000', '1000 - '+ str(bin_4), str(bin_4) + ' - ' + str(bin_5), \
        str(bin_5) + ' - ' + str(bin_6), str(bin_6) + ' - ' + str(covid_max_int)])

    print('')
    print('')
    print('Do you want to save the map as a png file to the current directory? [y/n]''\n')
    save_fig = msvcrt.getch()
    print('The map will be displayed shortly.')
    if save_fig.lower() == b'y':
        fig1 = plt.gcf()
        #Change dpi to higher value for higher res (dpi*2 = size*4!!!). \
        #This currently gives ~1000 x 600, depends on local settings though.
        filename_s = 'image.png'
        fig1.savefig(filename_s, bbox_inches='tight', pad_inches=0.1, \
                    optimize=True, dpi=50)

    plt.show()


def save_map_to_png():
    """Save geo maps as png files for every date in date row.
    """
    covid_max_int = int(COVID_MAX)

    for index in range(3, COVID_WORLD.shape[1]):
    #Sequence that plots and saves png for every date in date row.
        norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
        cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

        #Change projection to Miller in order to remove map distortions. \
        #Chk alt classifiers >> https://pysal.org/mapclassify/_modules/mapclassify/classifiers.html
        ax1 = geoplot.polyplot(COVID_WORLD, gcrs.Miller(), figsize=(30, 15))

        #data_col is the respective date column selected.
        data_col = COVID_WORLD.iloc[:, index]
        #Convert to date to provide as secondary title.
        data_col_header = (data_col.reset_index()).columns.values[1]
        chart_date = datetime.strptime(str(data_col_header), '%m/%d/%y').strftime('%m/%d/%y')

        ax1.set_title('Covid-19 Cases by Country', fontsize=28, loc='left')
        ax1.text(0.88, 0.93, str(chart_date), color='blue', \
                alpha=0.7, fontsize=40, transform=ax1.transAxes)
        ax1.text(0.55, 0.01, 'Data sources aggregated by JHU CSSE @ \
            https://github.com/CSSEGISandData/COVID-19', color='#004C74', alpha=1, fontsize=14, \
            transform=ax1.transAxes)

        #Customized data bins
        bin_4 = round(int(COVID_MAX*0.01/1000)*1000)
        bin_5 = round(int(COVID_MAX*0.1/10000)*10000)
        bin_6 = round(int(COVID_MAX*0.5/10000)*10000)
        scheme = mapclassify.UserDefined(data_col, bins=[10, 300, 1000, \
            round(int(COVID_MAX*0.01/1000)*1000), \
            round(int(COVID_MAX*0.1/10000)*10000), \
            round(int(COVID_MAX*0.5/10000)*10000), covid_max_int])

        geoplot.choropleth(COVID_WORLD, hue=data_col, scheme=scheme, legend=True, \
            legend_kwargs={'loc':'lower left', 'fontsize':16}, cmap=cmap, norm=norm, ax=ax1, \
            extent=(-180, -60, 180, 90), legend_labels=['0 - 10', '10 - 300', '300 - 1000', \
            '1000 - '+ str(bin_4), str(bin_4) + ' - ' + str(bin_5), \
            str(bin_5) + ' - ' + str(bin_6), str(bin_6) + ' - ' + str(covid_max_int)])

        fig1 = plt.gcf()


        #Reformat column header for filenames.
        data_col_header_formatted = datetime.strptime(str(data_col_header), '%m/%d/%y').date()

        #Create dir for png files.
        if not os.path.exists(DIR_NAME):
            os.mkdir(DIR_NAME)
            print("Directory ", DIR_NAME, " Created ")

        #Change dpi to higher value for higher res (dpi*2 = size*4!!!). \
        #This currently gives ~1000 x 600, depends on local settings though.
        filename = (NAME_IMAGE + str(data_col_header_formatted) + '.png')
        fig1.savefig(DIR_NAME + '/' + filename, bbox_inches='tight', pad_inches=0.1, \
            optimize=True, dpi=50)

        plt.close('all')

def png_to_gif():
    """Make gif file from png files created before.
    """
    #Create list for length of sequences of gif
    file_number = len([name for name in os.listdir(DIR_NAME) \
        if os.path.isfile(os.path.join(DIR_NAME, name))])
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
    fp_in = DIR_NAME + '/' + NAME_IMAGE + '2020-*.png'
    fp_out = DIR_NAME + '/' + NAME_IMAGE + '.gif'

    img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
    img.save(fp=fp_out, format='GIF', append_images=imgs, save_all=True, duration=list_dur, \
            loop=1, optimize=True, dpi=50)



COVID_MAX, COVID_WORLD, COVID_LAST = get_and_process_data()
OUT_OPTION, COL_VAL, NAME_IMAGE, DIR_NAME = get_output_type()

if OUT_OPTION == b'3':
    show_map()
elif OUT_OPTION == b'1':
    save_map_to_png()
    png_to_gif()
