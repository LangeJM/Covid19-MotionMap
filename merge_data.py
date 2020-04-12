import geopandas
import pandas

import covid_getdata
from covid_getdata import data_covid
import worldall_getshape
from worldall_getshape import world_sov


#Merge data on shapefile so that new file retains geodataframe format
covid_world = world_sov.merge(data_covid, on='Country_Region', how='outer').reset_index()


#Override NaN values with zero and 9999 where index column, respectively 
covid_world[covid_world.columns[3:]] = covid_world[covid_world.columns[3:]].fillna(0)
covid_world['index'] = covid_world['index'].fillna(9999)

#Determine max data value for scaling and legend (selecting last column of data frame)
covid_max = covid_world.iloc[:,-1].max()

#Reenforce geodataframe format (to avoid exception, however, it seems this is not a solid fix)
covid_world = geopandas.GeoDataFrame(
    covid_world, geometry=covid_world['geometry'])


