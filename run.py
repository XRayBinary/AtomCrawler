import ssl
import re
import requests
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import json

context = ssl.create_default_context()
context.set_ciphers('TLSv1.2')

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
adapter = SSLAdapter()
session.mount('https://', adapter)



def get_countries():

    url = 'https://pris.iaea.org/PRIS/CountryStatistics/CountryStatisticsLandingPage.aspx'

    response = session.get(url)

    countries_list = []
    countries_url_list = []

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'id': re.compile('^MainContent_rptSideNavigation_hypNavigation_')})

        for link in links:

            link_text = link.get_text(strip=True)
            link_href = link.get('href')

            countries_list.append(link_text)
            countries_url_list.append(link_href)

    data_dicts = dict(zip(countries_list, countries_url_list))

    with open('countries.json', "w") as f:
                json.dump(data_dicts, f, indent=4)


def get_nuclearPlant():

    with open('countries.json', "r") as f:
        countries = json.load(f)

    for country, path in countries.items():     

        response = session.get(path)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

        else:
            
            print(f"Error al acceder a la página: {response.status_code}")


def get_nuclearPlantData():

    url = 'https://pris.iaea.org/PRIS/CountryStatistics/ReactorDetails.aspx?current=153'

    response = session.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        reactor_name = soup.find('span', {'id': 'MainContent_MainContent_lblReactorName'}).text

        table = soup.find('table', {'class': 'active'})

        rows = table.find_all('tr')
        headers = rows[0].find_all('th')

        column_headers = [header.get_text(strip=True) for header in headers]

        with open(f'{reactor_name}.json', "w") as f:
            f.write("")

        keys = column_headers
        data = []

        for row in rows[2:]:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)

        for row in data:

            data_dicts = [dict(zip(keys, row)) for row in data]

            with open(f'{reactor_name}.json', "w") as f:
                json.dump(data_dicts, f, indent=4)

    else:
        print(f"Error al acceder a la página: {response.status_code}")



get_nuclearPlant()
