from openfisca_us.model_api import *


class in_base_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN base exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(3)-(4)

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.exemptions
        num_filers = tax_unit("num", period)
        base_exemption = p.base.amount
        dependents = tax_unit("tax_unit_dependents", period)
        return (dependents + num_filers) * base_exemption
