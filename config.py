
class Config:
    # have to update it every time :D (I just do not want to write my password here)
    COOKIE = ''

    # header to be sent in each request
    HEADER = {
        'Connection': 'keep-alive',
        'Cookie': f'PHPSESSID={COOKIE}',
        'Host': '37.224.41.209',
    }

    # time to wait between each request
    DEFAULT_SLEEP_TIME = 0.25

    # number of allowed fails per request
    ALLOWED_FAIL_COUNTER = 3

    # base url for site (specific to the HMIS system we use, called 'Imdad')
    BASE_URL = ''

    # url for pages (concatenated with BASE_URL)
    CASH_SERVICES_URL = 'services.php'
    CASH_X_RAY_URL = 'rays.php'
    CASH_LAB_URL = 'anas.php'

    COMPANY_SERVICES_URL = 'contract_add.php'
    COMPANY_X_RAY_AND_LAB_URL = 'contract_add1.php'

    # excel file & sheet names for both cash & company specific file
    CASH_SERVICES_FILE_NAME = 'ALL CASH SERVICES.xlsx'
    CASH_SERVICES_SHEET_NAME = 'Services'
    CASH_X_RAY_SHEET_NAME = 'X-Ray'
    CASH_LAB_SHEET_NAME = 'Lab'

    COMPANY_SERVICES_FILE_NAME = 'ALL [COMPANY_NAME] SERVICES.xlsx'
    COMPANY_SERVICES_SHEET_NAME = 'Services'
    COMPANY_X_RAY_AND_LAB_SHEET_NAME = 'X-Ray & Lab'
    
    COMPANY_SERVICES_DETAILS_FILE_NAME = 'ALL [COMPANY_NAME] SERVICES DETAILS.xlsx'
    COMPANY_SERVICES_DETAILS_SHEET_NAME = 'Services'
    COMPANY_X_RAY_AND_LAB_DETAILS_SHEET_NAME = 'X-Ray & Lab'

    COMPANY_MATCHED_X_RAY_AND_LAB_FILE_NAME = 'ALL [COMPANY_NAME] MATCHED X-RAY & LAB.xlsx'
    COMPANY_MATCHED_X_RAY_AND_LAB_SHEET_NAME = 'X-Ray & Lab'