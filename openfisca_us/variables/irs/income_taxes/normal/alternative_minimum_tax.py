from openfisca_us.model_api import *


class alternative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alternative Minimum Tax"
    unit = "currency-USD"
    documentation = "Total liability for the Alternative Minimum Tax"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/55#a"

    def formula(tax_unit, period, parameters):
        return max_(
            0,
            (
                tax_unit("tentative_minimum_tax", period),
                -tax_unit("regular_tax", period),
            ),
        )

class taxable_excess(Variable):
    value_type = float
    entity = TaxUnit
    label = "\"Taxable excess\" for AMT"
    unit = "currency-USD"
    documentation = "Alternative minimum taxable income over the exemption"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    def formula(tax_unit, period, parameters):
        pass

class amt_foreign_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "AMT foreign tax credit"
    unit = "currency-USD"
    documentation = "Alternative Minimum Tax foreign tax credit from Form 6251"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("e62900", period)


def apply_usc_26_55_b_1_A(tax_unit, parameters, period, income):
    tmt = parameters(period).irs.income_taxes.normal.amt.tmt
    threshold = tmt.threshold * (where(tax_unit("sep", period), tmt.separate_filer_multiplier, 1))
    return (
        tmt.rate.lower * min_(income, threshold)
        + tmt.rate.higher * max_(0, income - threshold)
    )

class net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain"
    unit = "currency-USD"
    definition_period = YEAR

class adjusted_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted net capital gain"
    unit = "currency-USD"
    definition_period = YEAR

class unrecaptured_s_1250_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Un-recaptured Section 1250 gain"
    unit = "currency-USD"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("e24515", period)


class tentative_minimum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tentative minimum tax"
    unit = "currency-USD"
    documentation = "A minimum tax boundary used in the calculation of AMT"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b"

    def formula(tax_unit, period, parameters):
        tmt = parameters(period).irs.income_taxes.normal.amt.tmt
        taxable_excess = tax_unit("taxable_excess", period)
        amount = apply_usc_26_55_b_1_A(tax_unit, parameters, period, taxable_excess)
        #(b)(3) Maximum rate of tax on net capital gain of noncorporate taxpayers

        #(b)(3) sections (a) through (e)
        reduced_excess = taxable_excess = min_(
            tax_unit("net_capital_gain", period),
            (
                tax_unit("adjusted_net_capital_gain", period)
                + tax_unit("unrecaptured_s_1250_gain", period)
            )
        )
        a = apply_usc_26_55_b_1_A(tax_unit, parameters, period, taxable_excess)
        b = 0

        foreign_tax_credit = tax_unit("amt_foreign_tax_credit", period)

        return amount - foreign_tax_credit
