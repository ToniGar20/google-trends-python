from pytrends.request import TrendReq
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g
import pandas as pd
import csv
import gspread


# Documentation of Google Trends categories
# https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories
TRENDS_CATEGORIES = {
    158: 'Mejora del hogar',
    950: 'Herramientas de construcción y eléctricas',
    828: 'Sistemas de climatización',
    1153: 'Fontanería',
    1232: 'Pintura de la casa y acabados',
    827: 'Puertas y ventanas',
    832: 'Revestimiento para suelos',
    1175: 'Tejados',
    48: 'Construcción y mantenimiento',
    471: 'Control de plagas',
    951: 'Cocinas',
    271: 'Electrodomésticos',
    137: 'Hogar y decoración de interiores',
    269: 'Jardinería y ajardinamiento',
    952: 'Piscinas, balnearios y spas',
    949: 'Servicios y suministros de limpieza',
    705: 'Servicios y productos de seguridad',
    270: 'Mobiliario doméstico',
    291: 'Mudanzas y traslados',
}

# Online markets to analize data
COUNTRIES = ['ES', 'IT', 'PT']


def get_trends(trend_category, country):
    if country == 'ES':
        pytrend = TrendReq(hl='es-ES')  # Spanish market
    elif country == 'IT':
        pytrend = TrendReq(hl='it-IT')  # Italy market
    elif country == 'PT':
        pytrend = TrendReq(hl='pt-PT')  # Portugal market
    else:
        print('El país para extraer datos no es correcto')
        return

    pytrend.build_payload(
        kw_list=[''],  # No keyword to fetch data of whole category
        cat=trend_category,
        timeframe='today 5-y',
        geo=country
    )
    data = pytrend.interest_over_time()
    data['category'] = TRENDS_CATEGORIES[trend_category]
    data['country'] = country
    del data['isPartial']
    return data


# Writing data into CSV
#
# Headers for file
file_header = ['date', 'trend_value', 'category', 'country']

with open('category-trends-results.csv', 'w') as file:
    file.truncate()  # Removing content of current CSV if there is old one
    writer = csv.writer(file)
    writer.writerow(file_header)

    # Country and category loops
    for item in COUNTRIES:
        for category in TRENDS_CATEGORIES:
            category_data = get_trends(category, item)
            print(category_data)
            category_data.to_csv('category-trends-results.csv', header=None, mode='a')

# Converting 'trend_value' data to int64
csv_data = pd.read_csv('category-trends-results.csv')
csv_data['trend_value'] = csv_data['trend_value'].astype(str).astype(int)

# Sending CSV data to Google SpreadSheet
#
# Data for autorization with user fo Google API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('py-for-gsheets-ed724968a63d.json', scope)
gc = gspread.authorize(credentials)

# Drive key and worksheet
# Full path: https://docs.google.com/spreadsheets/d/10RBqKVfXuNViou5LUBjE3-tHfqjkZckEIncnHBlJOMk/
spreadsheet_key = '10RBqKVfXuNViou5LUBjE3-tHfqjkZckEIncnHBlJOMk'
wks_name = 'Data'

# Reading CSV and writing df2gspread package
df = pd.read_csv('category-trends-results.csv')
d2g.upload(df, spreadsheet_key, wks_name, credentials=credentials, row_names=True)
