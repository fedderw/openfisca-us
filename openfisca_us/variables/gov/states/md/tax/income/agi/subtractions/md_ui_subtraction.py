from openfisca_us.model_api import *


class md_ui_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    abel = "MD unemployment insurance subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = ""
