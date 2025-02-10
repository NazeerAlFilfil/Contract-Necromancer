from ftfy import fix_text
import pandas as pd
import re

class Utility:
    def convert_to_clean_dataframe(normal_list: list) -> pd.DataFrame:
        dataframe = pd.DataFrame(normal_list)
            
        dataframe = dataframe.map(Utility.remove_illegal_characters)

        return dataframe

    def remove_illegal_characters(text) -> str:
        return fix_text(text) if isinstance(text, str) else text
    
    def write_to_excel(filename: str, dataframes: list[pd.DataFrame], sheetnames: list[str]):
        # check if dataframes number is equal to sheetnames provided (each in separate sheet)
        if len(dataframes) == len(sheetnames):
            # print to excel with separate excel sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for index in range(len(dataframes)):
                    dataframes[index].to_excel(writer, index=False, sheet_name=sheetnames[index])
        else:
            print(f'Error: Number of dataframes [{len(dataframes)}] provided does not equal to the number of sheetnames [{len(sheetnames)}]!')

    def search_in_list(service: dict, service_key: str, search_list: list):
        for value in search_list:
            service_name = re.sub(r'[\u200e]', '', service[service_key]).lower()
            value_name = re.sub(r'[\u200e]', '', value[service_key]).lower()

            if service_name == value_name:
                return value['code']
            
        return None
    
    def match_insurance_with_cash(insurance, cash):
        '''
        This function takes the services of both insurance and cash, then match the x-ray and laboratory services with the system code from the cash services.
        '''

        # import here to avoid dependancy hell
        from cash_services import CashServices
        from company_services import CompanyServices

        insurance: CompanyServices
        cash: CashServices

        for service in insurance.x_ray_and_lab_services_details:
            if service['naphies_type'] == 'imaging':
                code = Utility.search_in_list(service=service, service_key='name', search_list=cash.x_ray_services)
            elif service['naphies_type'] == 'laboratory':
                code = Utility.search_in_list(service=service, service_key='name', search_list=cash.lab_services)
            else:
                code = Utility.search_in_list(service=service, service_key='name', search_list=cash.x_ray_services)
                if not code:
                    code = Utility.search_in_list(service=service, service_key='name', search_list=cash.lab_services)

            service['system code'] = code

        # print the result
        insurance.write_x_ray_lab_details()
