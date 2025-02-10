import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
from config import Config
from utility import Utility

class CompanyServices:
    def __init__(self, company_id: str, company_name: str, create_new: bool = False, create_new_details: bool = False):
        self.company_id = company_id
        self.company_name = company_name

        self.create_new = create_new
        self.create_new_details = create_new_details

        self.regular_services = []
        self.x_ray_and_lab_services = []
        
        self.regular_services_details = []
        self.x_ray_and_lab_services_details = []

        if self.create_new and self.create_new_details:
            #self.get_services(get_regular_services = True, get_regular_services_details = False, get_x_ray_and_lab = True, get_x_ray_details = False, get_lab_details = False)
            self.get_services(get_regular_services = True, get_regular_services_details = True, get_x_ray_and_lab = True, get_x_ray_and_lab_details = True)
        elif self.create_new:
            self.get_services(get_regular_services = True, get_x_ray_and_lab = True)
        elif self.create_new_details:
            self.get_services(get_regular_services_details = True, get_x_ray_and_lab_details = True)
        else:
            self.get_services()

    def get_services(self, get_regular_services: bool = False, get_regular_services_details: bool = False, get_x_ray_and_lab: bool = False, get_x_ray_and_lab_details: bool = False):
        regular_services = []
        x_ray_and_lab_services = []

        regular_services_details = []
        x_ray_and_lab_services_details = []

        # generate company name
        COMPANY_FILE_NAME = self.company_name.join(Config.COMPANY_SERVICES_FILE_NAME.split('[COMPANY_NAME]'))
        COMPANY_DETAILS_FILE_NAME = self.company_name.join(Config.COMPANY_SERVICES_DETAILS_FILE_NAME.split('[COMPANY_NAME]'))

        if self.create_new:
            # services
            if get_regular_services:
                regular_services = self._get_regular_services()
                self.regular_services = regular_services

            if get_x_ray_and_lab:
                x_ray_and_lab_services = self._get_x_ray_and_lab_services()
                self.x_ray_and_lab_services = x_ray_and_lab_services

            # convert to pandas dataframe
            regular_services_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.regular_services)
            x_ray_and_lab_services_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.x_ray_and_lab_services)

            # print to excel
            Utility.write_to_excel(
                filename=COMPANY_FILE_NAME,
                dataframes=[regular_services_df, x_ray_and_lab_services_df],
                sheetnames=[Config.COMPANY_SERVICES_SHEET_NAME, Config.COMPANY_X_RAY_AND_LAB_SHEET_NAME],
            )

            # ----- ----- ----- ----- ----- #

        if self.create_new_details:
            # read file if we don't want to re-create the file (and it exist)
            if not self.create_new:
                self._read_services(COMPANY_FILE_NAME)

            # services details
            if get_regular_services_details:
                regular_services_details = self._get_regular_services_details()
                self.regular_services_details = regular_services_details

            if get_x_ray_and_lab_details:
                x_ray_and_lab_services_details = self._get_x_ray_and_lab_services_details()
                self.x_ray_and_lab_services_details = x_ray_and_lab_services_details

            # convert to pandas dataframe
            regular_services_details_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.regular_services_details)
            x_ray_and_lab_services_details_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.x_ray_and_lab_services_details)

            # print to excel
            Utility.write_to_excel(
                filename=COMPANY_DETAILS_FILE_NAME,
                dataframes=[regular_services_details_df, x_ray_and_lab_services_details_df],
                sheetnames=[Config.COMPANY_SERVICES_DETAILS_SHEET_NAME, Config.COMPANY_X_RAY_AND_LAB_DETAILS_SHEET_NAME],
            )
        
            # just in case
            self.create_new = False
        
        if not self.create_new:
            self._read_services(COMPANY_FILE_NAME)

        if not self.create_new_details:
            self._read_services_details(COMPANY_DETAILS_FILE_NAME)

        return self.regular_services, self.regular_services_details, self.x_ray_and_lab_services, self.x_ray_and_lab_services_details

    def write_x_ray_lab_details(self):
        COMPANY_MATCHED_X_RAY_AND_LAB_FILE_NAME = self.company_name.join(Config.COMPANY_MATCHED_X_RAY_AND_LAB_FILE_NAME.split('[COMPANY_NAME]'))

        # convert to pandas dataframe
        x_ray_and_lab_services_details_df: pd.DataFrame = Utility.convert_to_clean_dataframe(self.x_ray_and_lab_services_details)

        # print to excel
        Utility.write_to_excel(
            filename=COMPANY_MATCHED_X_RAY_AND_LAB_FILE_NAME,
            dataframes=[x_ray_and_lab_services_details_df],
            sheetnames=[Config.COMPANY_MATCHED_X_RAY_AND_LAB_SHEET_NAME],
        )

    def _read_services(self, COMPANY_FILE_NAME: str):
        # check if file exist
        if os.path.exists(COMPANY_FILE_NAME):
            dfs = pd.read_excel(COMPANY_FILE_NAME, sheet_name=None, engine='openpyxl', dtype=str)
            
            # read data from sheets
            regular_services_df = dfs[Config.COMPANY_SERVICES_SHEET_NAME]
            x_ray_and_lab_services_df = dfs[Config.COMPANY_X_RAY_AND_LAB_SHEET_NAME]

            # convert df to regualr list with dictionaries
            self.regular_services = regular_services_df.to_dict(orient='records')
            self.x_ray_and_lab_services = x_ray_and_lab_services_df.to_dict(orient='records')
        else:
            print(f'The file ({COMPANY_FILE_NAME}) not found.')

    def _read_services_details(self, COMPANY_DETAILS_FILE_NAME: str):
        # check if file exist
        if os.path.exists(COMPANY_DETAILS_FILE_NAME):
            dfs = pd.read_excel(COMPANY_DETAILS_FILE_NAME, sheet_name=None, engine='openpyxl', dtype=str)
            
            # read data from sheets
            regular_services_details_df = dfs[Config.COMPANY_SERVICES_DETAILS_SHEET_NAME]
            x_ray_and_lab_services_details_df = dfs[Config.COMPANY_X_RAY_AND_LAB_DETAILS_SHEET_NAME]

            # convert df to regualr list with dictionaries
            self.regular_services_details = regular_services_details_df.to_dict(orient='records')
            self.x_ray_and_lab_services_details = x_ray_and_lab_services_details_df.to_dict(orient='records')
        else:
            print(f'The file ({COMPANY_DETAILS_FILE_NAME}) not found.')

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
        print(f'Getting {self.company_name} Services...')

        while run:
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{Config.COMPANY_SERVICES_URL}?page={page}&com_id={self.company_id}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                first_table = page_soup.find('table')
                rows = first_table.find_all('tr')
                rows = rows[6:-1]

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
                    service['price'] = tds[2].contents[0]
                    service['discount'] = tds[3].contents[0]
                    service['net'] = tds[4].contents[0]
                    service['approval'] = tds[5].contents[0]
                    service['class'] = tds[6].contents[0]
                    service['edit_link'] = tds[7].find_all('a')[0].attrs.get('href')
                    service['delete_link'] = tds[8].find_all('a')[0].attrs.get('href')

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
        print(f'Completed {self.company_name} Services!\n')

        return services

    def _get_x_ray_and_lab_services(self):
        # list to save services
        services = []

        # allowed fail counter
        fail_counter = Config.ALLOWED_FAIL_COUNTER

        # track which page we are on
        page = 1

        # flag to know when to stop
        run = True
        
        # debug
        print(f'Getting {self.company_name} X-Ray & Lab Services...')

        while run:
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{Config.COMPANY_X_RAY_AND_LAB_URL}?page={page}&com_id={self.company_id}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                first_table = page_soup.find('table')
                rows = first_table.find_all('tr')
                rows = rows[6:-1]

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
                    service['price'] = tds[2].contents[0]
                    service['discount'] = tds[3].contents[0]
                    service['net'] = tds[4].contents[0]
                    service['approval'] = tds[5].contents[0]
                    service['class'] = tds[6].contents[0]
                    service['edit_link'] = tds[7].find_all('a')[0].attrs.get('href')
                    service['delete_link'] = tds[8].find_all('a')[0].attrs.get('href')

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
        print(f'Completed {self.company_name} X-Ray & Lab Services!\n')

        return services

    def _get_regular_services_details(self):
        # list to save services
        services = []

        # allowed fail counter
        fail_counter = Config.ALLOWED_FAIL_COUNTER
        
        # debug
        print(f'Getting {self.company_name} Services Details...')

        if not self.regular_services:
            print(f'Error: Services list for {self.company_name} not available!')
            return []

        for index in range(len(self.regular_services)):
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{self.regular_services[index]['edit_link']}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                first_table = page_soup.find('table')
                rows = first_table.find_all('tr')
                rows = rows[1:-1]

                # get values from input & select elements
                details_list = []
                for row in rows:
                    service_input = row.find('input')

                    if service_input:
                        details_list.append(service_input.attrs.get('value'))
                    else:
                        service_selected_option = row.find('option', selected=True)
                        if service_selected_option:
                            details_list.append(service_selected_option.attrs.get('value'))
                        else:
                            details_list.append('')

                service_details = {}

                service_details['name'] = details_list[0]
                service_details['code'] = details_list[1]
                service_details['category'] = details_list[2]
                service_details['price'] = details_list[3]
                service_details['discount'] = details_list[4]
                service_details['approval'] = details_list[5]
                service_details['class'] = details_list[6]
                service_details['vat'] = details_list[7]
                service_details['recheck'] = details_list[8]
                service_details['naphies_name'] = details_list[9]
                service_details['naphies_code'] = details_list[10]
                service_details['naphies_type'] = details_list[11]

                services.append(service_details)

                # debug
                print(f'[{self.regular_services[index]['name']}] details retrieved.')
                
                time.sleep(Config.DEFAULT_SLEEP_TIME) # sleep, so server don't cry & crash

                # reset fail counter
                fail_counter = Config.ALLOWED_FAIL_COUNTER
            except Exception as exception:
                if fail_counter > 0:
                    print(f'Error: [{exception}]')
                    print(f'Failed to get [{self.regular_services[index]['name']}], Trying again...')
                    print(f'Number of remaining tries: [{fail_counter}]')
                    index -= 1
                    fail_counter -= 1
                else:
                    print(f'Failed to finish request')
                    print(f'Error: [{exception}]')

        # debug
        print(f'Completed {self.company_name} Services Details!\n')

        return services
    
    def _get_x_ray_and_lab_services_details(self):
        # list to save services
        services = []

        # allowed fail counter
        fail_counter = Config.ALLOWED_FAIL_COUNTER
        
        # debug
        print(f'Getting {self.company_name} X-Ray & Lab Details...')

        if not self.x_ray_and_lab_services:
            print(f'Error: Services list for {self.company_name} not available!')
            return []

        for index in range(len(self.x_ray_and_lab_services)):
            try:
                # construct url
                URL = f'{Config.BASE_URL}/{self.x_ray_and_lab_services[index]['edit_link']}'

                # request page
                response = requests.get(url=URL, headers=Config.HEADER)
                response.encoding = 'utf-8'

                # get content we want
                html_content = response.text
                page_soup = BeautifulSoup(html_content, 'html.parser')
                first_table = page_soup.find('table')
                rows = first_table.find_all('tr')
                rows = rows[1:-1]

                # get values from input & select elements
                details_list = []
                for row in rows:
                    service_input = row.find('input')

                    if service_input:
                        details_list.append(service_input.attrs.get('value'))
                    else:
                        service_selected_option = row.find('option', selected=True)
                        if service_selected_option:
                            details_list.append(service_selected_option.attrs.get('value'))
                            service_select = row.find('select')
                            if service_select.attrs.get('name') == 's_id':
                                details_list.append(service_selected_option.contents[0])
                        else:
                            details_list.append('')

                service_details = {}

                service_details['service_value'] = details_list[0]
                service_details['name'] = details_list[1]
                service_details['code'] = details_list[2]
                service_details['price'] = details_list[3]
                service_details['discount'] = details_list[4]
                service_details['approval'] = details_list[5]
                service_details['class'] = details_list[6]
                service_details['naphies_name'] = details_list[7]
                service_details['naphies_code'] = details_list[8]
                service_details['naphies_type'] = details_list[9]

                services.append(service_details)

                # debug
                print(f'[{self.x_ray_and_lab_services[index]['name']}] details retrieved.')
                
                time.sleep(Config.DEFAULT_SLEEP_TIME) # sleep, so server don't cry & crash

                # reset fail counter
                fail_counter = Config.ALLOWED_FAIL_COUNTER
            except Exception as exception:
                if fail_counter > 0:
                    print(f'Error: [{exception}]')
                    print(f'Failed to get [{self.x_ray_and_lab_services[index]['name']}], Trying again...')
                    print(f'Number of remaining tries: [{fail_counter}]')
                    index -= 1
                    fail_counter -= 1
                else:
                    print(f'Failed to finish request')
                    print(f'Error: [{exception}]')

        # debug
        print(f'Completed {self.company_name} X-Ray & Lab Details!\n')

        return services