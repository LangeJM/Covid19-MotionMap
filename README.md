# Covid19-MotionMap
### Python Script to create gif geo map (motion map)  based on data from CSSEGIS (Johns Hopkins) 

This is my first Python project (and actually coding projects aside of some GoogleAppScript scripts) with the use case of creating a gif geo map (motion map) of Covid19 cases by country as aggregated by [CSSEGIS](https://github.com/CSSEGISandData/COVID-19).

Libraries/ packages/ modules used: geopandas, geoplot, pandas, mapclassify, matplotlib, pyplot, datetime, os, imageio, glob, PIL, requests, fiona. 
Refer to requirements.txt

I encountered many issues with dependencies between libraries. It seems it is not easy to get geopandas running. The only thing that worked was an installation via Anaconda [4.7.12](https://repo.continuum.io/archive/).

What the script does:
1. Get data of Covid19 cases by day and country, get world shape file from Natural Earth
2. Clean data and merge both sources
3. Plot geomap and create png per day
4. Create gif of all pngs


#### Feedback very welcome!





