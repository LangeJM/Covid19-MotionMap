###Acquire shapefile as part of zip file via url 

import geopandas
import requests
import fiona

url = 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
request = requests.get(url)
b = bytes(request.content)
with fiona.BytesCollection(b) as f:
    crs = f.crs
    world_all = geopandas.GeoDataFrame.from_features(f, crs=crs)
    

##Cleaning of data
#We only need two columns, 'SOVEREIGNT' and 'geometry'
world_sov = world_all.filter(items=['ADMIN', 'geometry'])
#Rename column 'SOVEREIGNT' to 'Country_Region', in order to align with data source
world_sov = world_sov.rename(columns={'ADMIN' : 'Country_Region'})
#Rename country to align with data source 
world_sov['Country_Region'] = world_sov['Country_Region'].replace({"SÃ£o TomÃ© and Principe":"Sao Tome and Principe"})


