from openfisca_us.model_api import *


class md_lump_sum_retirement_distribution(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Lump Sum Retirement Distribution"
    unit = USD
    documentation = "LUMP SUM DISTRIBUTION FROM A QUALIFIED RETIREMENT PLAN."
    definition_period = YEAR

    # Ordinary income portion of distribution from Form 1099R reported on federal Form 4972 (taxable amount less capital gain amount - line 1) worksheet 12A

    # capital gain portion of distribution from Form 1099R

    # 40% of capital gain portion of distribution from Form 1099R

    # Add lines 1 and 2.
