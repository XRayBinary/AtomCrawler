import ssl
import re
import requests
import time
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

    url = 'https://pris.iaea.org/'

    with open('countries.json', "r") as f:
        countries = json.load(f)

    for country, path in countries.items():     

        url_country = url + path
        response = session.get(url_country)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table', {'class': 'tablesorter'})

            rows = table.find_all('tr')
            headers = rows[0].find_all('th')

            data = []

            for row in rows[1:]:
                cells = row.find_all('td')
                name = cells[0].get_text(strip=True)
                row_data = [cell.get_text(strip=True) for cell in cells[1:]]
                data.append(row_data)
                print(name)
                print(row_data)


        else:
            
            print(f"Error al acceder a la página: {response.status_code}")
        
        time.sleep(2)

def get_nuclearPlantData():

    url = 'https://pris.iaea.org/PRIS/CountryStatistics/ReactorDetails.aspx?current=3'

    response = session.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        reactor_name = soup.find('span', {'id': 'MainContent_MainContent_lblReactorName'}).text

        table = soup.find('table', {'class': 'active'})

        rows = table.find_all('tr')

        final_headers = []

        headers = rows[0].find_all('th')
        sub_headers = rows[1].find_all('th')

        n_cols = 0

        for header in headers:

            if header.get('colspan'):

                for i in range(n_cols, n_cols + int(header.get('colspan'))):
                    if i < len(sub_headers):
                        final_headers.append(f'{header.get_text(strip=True)}_{sub_headers[i].get_text(strip=True)}')
                
                n_cols = n_cols + int(header.get('colspan'))
            else:
                final_headers.append(header.get_text(strip=True))


        with open(f'{reactor_name}_AnualData.json', "w") as f:
            f.write("")

        keys = final_headers

        data = []

        for row in rows[2:]:
            cells = row.find_all('td')

            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)

        for row in data:

            data_dicts = [dict(zip(keys, row)) for row in data]

            with open(f'{reactor_name}_AnualData.json', "w") as f:
                json.dump(data_dicts, f, indent=4)

    else:
        print(f"Error al acceder a la página: {response.status_code}")



get_nuclearPlantData()
