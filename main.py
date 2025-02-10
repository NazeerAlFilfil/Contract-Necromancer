from cash_services import CashServices
from company_services import CompanyServices
from utility import Utility

cash_services = CashServices(
    create_new=False,
)

insurance_services = CompanyServices(
        company_id='1',
        company_name='Insurance',
        create_new=True,
        create_new_details=True,
    )

Utility.match_insurance_with_cash(insurance=insurance_services, cash=cash_services)