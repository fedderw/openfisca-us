from openfisca_core.parameters import (
    ParameterNode,
    Parameter,
    ParameterAtInstant,
)
from openfisca_core.periods import period, instant
from openfisca_core.periods.period_ import Period
from openfisca_tools.reforms import get_parameter
from numpy import floor, ceil


def uprate_parameters(root: ParameterNode) -> ParameterNode:
    """Uprates parameters according to their metadata.

    Args:
        root (ParameterNode): The root of the parameter tree.

    Returns:
        ParameterNode: The same root, with uprating applied to descendants.
    """

    for parameter in root.get_descendants():
        if isinstance(parameter, Parameter):
            if "uprating" in parameter.metadata:
                uprating_parameter = get_parameter(
                    root, parameter.metadata["uprating"]["parameter"]
                )
                # Start from the latest value
                last_instant = instant(parameter.values_list[0].instant_str)
                # For each defined instant in the uprating parameter
                for entry in uprating_parameter.values_list[::-1]:
                    entry_instant = instant(entry.instant_str)
                    # If the uprater instant is defined after the last parameter instant
                    if entry_instant > last_instant:
                        # Apply the uprater and add to the parameter
                        value_at_start = parameter(last_instant)
                        uprater_at_start = uprating_parameter(last_instant)
                        uprater_at_entry = uprating_parameter(entry_instant)
                        uprated_value = (
                            value_at_start
                            * uprater_at_entry
                            / uprater_at_start
                        )
                        if "rounding" in parameter.metadata["uprating"]:
                            rounding = parameter.metadata["uprating"][
                                "rounding"
                            ]
                            if "absolute" in rounding:
                                if "method" in rounding:
                                    if rounding["method"] == "upwards":
                                        method = ceil
                                    elif rounding["method"] == "downwards":
                                        method = floor
                                else:
                                    method = round
                                uprated_value = (
                                    method(
                                        uprated_value / rounding["absolute"]
                                    )
                                    * rounding["absolute"]
                                )
                        parameter.values_list.append(
                            ParameterAtInstant(
                                parameter.name,
                                entry.instant_str,
                                data=uprated_value,
                            )
                        )
                parameter.values_list.sort(
                    key=lambda x: x.instant_str, reverse=True
                )
    return root


def add_tax_cola(parameters: ParameterNode) -> ParameterNode:
    """Adds the Cost-of-Living-Adjustment for tax thresholds as specified in U.S.C Title 26 Section 1(f)(3).

    Args:
        parameters (ParameterNode): Parameter tree root

    Returns:
        ParameterNode: Modified root
    """

    cpi = parameters.bls.c_cpi_u
    average_cpi_values = {}

    # 1(f)(6)(B) specifies that the C-CPI-U for a calendar year is the average over the
    # 12-month period ending on 31 August of that year.

    for year in range(2011, 2021):
        time_period: Period = period(f"year:{year - 1}-09-01")
        monthly_values = []
        for month in time_period.get_subperiods("month"):
            value_at_month_start = cpi(month.start)
            monthly_values += [value_at_month_start]
        average_cpi = sum(monthly_values) / len(monthly_values)
        average_cpi_values[f"{year}-01-01"] = float(average_cpi)

    parameters.bls.add_child(
        "tax_year_cpi",
        Parameter(
            "tax_year_cpi",
            {
                "description": "Average C-CPI-U for the tax year",
                "values": average_cpi_values,
                "metadata": {
                    "unit": "currency-USD",
                },
            },
        ),
    )

    return parameters
