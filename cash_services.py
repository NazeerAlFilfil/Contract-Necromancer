import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
from config import Config
from utility import Utility

class CashServices:
    def __init__(self, create_new: bool = False):
        self.create_new = create_new

        self.regular_services = []
        self.x_ray_services = []
        self.lab_services = []

        if self.create_new:
            self.get_services(get_regular_services = True, get_x_ray = True, get_lab = True)
        else:
            self.get_services()

    def get_services(self, get_regular_services: bool = False, get_x_ray: bool = False, get_lab: bool = False):
        regular_services = []
        x_ray_services = []
        lab_services = []

        if self.create_new:
            if get_regular_services:
                regular_services = self._get_regular_services()
                self.regular_services = regular_services

            if get_x_ray:
                x_ray_services = self._get_x_ray_services()
                self.x_ray_services = x_ray_services

            if get_lab:
                lab_services = self._get_lab_services()
                self.lab_services = lab_services

            # convert to pandas dataframe
            regular_services_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.regular_services)
            x_ray_services_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.x_ray_services)
            lab_services_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.lab_services)

            # print to excel
            Utility.write_to_excel(
                filename=Config.CASH_SERVICES_FILE_NAME,
                dataframes=[regular_services_df, x_ray_services_df, lab_services_df],
                sheetnames=[Config.CASH_SERVICES_SHEET_NAME, Config.CASH_X_RAY_SHEET_NAME, Config.CASH_LAB_SHEET_NAME],
            )
        
            # just in case
            self.create_new = False
        else:
            # check if file exist
            if os.path.exists(Config.CASH_SERVICES_FILE_NAME):
                dfs = pd.read_excel(Config.CASH_SERVICES_FILE_NAME, sheet_name=None, engine='openpyxl', dtype=str)
                
                # read data from sheets
                regular_services_df = dfs[Config.CASH_SERVICES_SHEET_NAME]
                x_ray_services_df = dfs[Config.CASH_X_RAY_SHEET_NAME]
                lab_services_df = dfs[Config.CASH_LAB_SHEET_NAME]

                # convert df to regualr list with dictionaries
                self.regular_services = regular_services_df.to_dict(orient='records')
                self.x_ray_services = x_ray_services_df.to_dict(orient='records')
                self.lab_services = lab_services_df.to_dict(orient='records')
            else:
                print(f'The file ({Config.CASH_SERVICES_FILE_NAME}) not found.')

        return self.regular_services, self.x_ray_services, self.lab_services

    def _get_regular_services(self):
        # list to save services
        services = []

        # allowed fail counter
        fail_counter = Config.ALLOWED_FAIL_COUNTER

        # track which page we are on
        page = 1

        # flag to know when to stop
        run = True
        
        # debug
        print('Getting Cash Services...')

        while run:
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{Config.CASH_SERVICES_URL}?page={page}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                first_table = page_soup.find('table')
                rows = first_table.find_all('tr')
                rows = rows[3:-1]

                # check if we are at last page (sometimes the message NO RESULTS FOUND is written inside the table)
                if len(rows) == 1 and 'NO RESULTS FOUND' in rows[0].find('td').contents[0]:
                    break

                # extract service information for each service
                for row in rows:
                    # find row data and discard irrelavent data
                    tds = row.find_all('td')
                    tds = tds[1:]

                    # assign content
                    service = {}
                    service['name'] = tds[0].contents[0]
                    service['code'] = tds[1].contents[0]
                    service['class'] = tds[2].contents[0]
                    service['price'] = tds[3].contents[0]
                    service['edit_link'] = tds[4].find_all('a')[0].attrs.get('href')
                    service['delete_link'] = tds[5].find_all('a')[0].attrs.get('href')

                    # add service
                    services.append(service)

                # debug
                print(f'Completed Page #{page}')

                # go to next page
                page += 1

                # if the rows are empty, it means we reached the last page
                if not rows:
                    run = False
                
                time.sleep(Config.DEFAULT_SLEEP_TIME) # sleep, so server don't cry & crash

                # reset fail counter
                fail_counter = Config.ALLOWED_FAIL_COUNTER
            except Exception as exception:
                if fail_counter > 0:
                    print(f'Error: [{exception}]')
                    print(f'Failed to get Page #{page}, Trying again...')
                    print(f'Number of remaining tries: [{fail_counter}]')
                    fail_counter -= 1
                else:
                    print(f'Failed to finish request')
                    print(f'Error: [{exception}]')
                    run = False

        # debug
        print('Completed Cash Services!\n')

        return services

    def _get_x_ray_services(self):
        # list to save services
        services = []

        # allowed fail counter
        fail_counter = Config.ALLOWED_FAIL_COUNTER

        # track which page we are on
        page = 1

        # flag to know when to stop
        run = True
        
        # debug
        print('Getting Cash X-Ray Services...')

        while run:
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{Config.CASH_X_RAY_URL}?page={page}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                rows = page_soup.find_all('tr')
                rows = rows[3:-1]

                # check if we are at last page (sometimes the message NO RESULTS FOUND is written inside the table)
                if len(rows) == 1 and 'NO RESULTS FOUND' in rows[0].find('td').contents[0]:
                    break

                # extract service information for each service
                for row in rows:
                    # find row data and discard irrelavent data
                    tds = row.find_all('td')
                    tds = tds[1:]

                    # assign content
                    service = {}
                    service['name'] = tds[0].contents[0]
                    service['code'] = tds[1].contents[0]
                    if tds[2].contents:
                        service['class'] = tds[2].contents[0]
                    else:
                        service['class'] = ''
                    service['price'] = tds[3].contents[0]
                    service['edit_link'] = tds[4].find_all('a')[0].attrs.get('href')
                    service['delete_link'] = tds[5].find_all('a')[0].attrs.get('href')

                    # add service
                    services.append(service)

                # debug
                print(f'Completed Page #{page}')

                # go to next page
                page += 1

                # if the rows are empty, it means we reached the last page
                if not rows:
                    run = False
                
                time.sleep(Config.DEFAULT_SLEEP_TIME) # sleep, so server don't cry & crash

                # reset fail counter
                fail_counter = Config.ALLOWED_FAIL_COUNTER
            except Exception as exception:
                if fail_counter > 0:
                    print(f'Error: [{exception}]')
                    print(f'Failed to get Page #{page}, Trying again...')
                    print(f'Number of remaining tries: [{fail_counter}]')
                    fail_counter -= 1
                else:
                    print(f'Failed to finish request')
                    print(f'Error: [{exception}]')
                    run = False

        # debug
        print('Completed Cash X-Ray Services!\n')

        return services

    def _get_lab_services(self):
        # list to save services
        services = []

        # allowed fail counter
        fail_counter = Config.ALLOWED_FAIL_COUNTER

        # track which page we are on
        page = 1

        # flag to know when to stop
        run = True
        
        # debug
        print('Getting Cash Lab Services...')

        while run:
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{Config.CASH_LAB_URL}?page={page}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                rows = page_soup.find_all('tr')
                rows = rows[3:-1]

                # check if we are at last page (sometimes the message NO RESULTS FOUND is written inside the table)
                if len(rows) == 1 and 'NO RESULTS FOUND' in rows[0].find('td').contents[0]:
                    break

                # extract service information for each service
                for row in rows:
                    # find row data and discard irrelavent data
                    tds = row.find_all('td')
                    tds = tds[1:]

                    # assign content
                    service = {}
                    service['name'] = tds[0].contents[0]
                    service['code'] = tds[1].contents[0]
                    if tds[2].contents:
                        service['class'] = tds[2].contents[0]
                    else:
                        service['class'] = ''
                    service['price'] = tds[3].contents[0]
                    service['edit_link'] = tds[4].find_all('a')[0].attrs.get('href')
                    service['delete_link'] = tds[5].find_all('a')[0].attrs.get('href')

                    # add service
                    services.append(service)

                # debug
                print(f'Completed Page #{page}')

                # go to next page
                page += 1

                # if the rows are empty, it means we reached the last page
                if not rows:
                    run = False
                
                time.sleep(Config.DEFAULT_SLEEP_TIME) # sleep, so server don't cry & crash

                # reset fail counter
                fail_counter = Config.ALLOWED_FAIL_COUNTER
            except Exception as exception:
                if fail_counter > 0:
                    print(f'Error: [{exception}]')
                    print(f'Failed to get Page #{page}, Trying again...')
                    print(f'Number of remaining tries: [{fail_counter}]')
                    fail_counter -= 1
                else:
                    print(f'Failed to finish request')
                    print(f'Error: [{exception}]')
                    run = False

        # debug
        print('Completed Cash Lab Services!\n')

        return services