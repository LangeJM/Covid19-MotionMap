import pandas

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
data_covid = pandas.read_csv(url, index_col=0)
data_covid = data_covid.drop(columns=['Lat', 'Long'])

##Cleaning of data##
#Rename'Country/Region' value 'West Bank and Gaza' to 'Israel', so we can merge with already existing 'Israel'. This is necessary as shape file doesn't list 'West Bank and Gaza'.
data_covid['Country/Region'] = data_covid['Country/Region'].replace({'West Bank and Gaza': 'Israel'})
#Aggregates numbers for countries that are divided into regions/states, such as Canada, China, US (or as manually created 'Israel')
data_covid = data_covid.groupby(['Country/Region'], as_index = False).sum(axis=0, skipna=True)
#Rename country column header to match lookup table that we maybe use later
data_covid = data_covid.rename(columns={'Country/Region' : 'Country_Region'})
#Delete hostorical/unique locations not mapped out 
data_covid = data_covid[(data_covid.Country_Region != 'Diamond Princess') & (data_covid.Country_Region != 'MS Zaandam') & (data_covid.Country_Region != 'Antarctica')]
#Rename countries in alignment with shapefile
data_covid["Country_Region"] = data_covid["Country_Region"].replace({"Bahamas":"The Bahamas","Burma" :"Myanmar","Congo (Brazzaville)" : "Republic of the Congo", "Congo (Kinshasa)" : "Democratic Republic of the Congo", "Cote d'Ivoire" : "Ivory Coast", "Holy See": "Vatican", "Korea, South": "South Korea", "North Macedonia": "Macedonia","Serbia":"Republic of Serbia", "Tanzania" : "United Republic of Tanzania", "Timor-Leste" : "East Timor", "US": "United States of America", "Taiwan*" : "Taiwan", "Eswatini":"eSwatini"})








