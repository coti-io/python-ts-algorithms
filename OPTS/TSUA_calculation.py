import math
#
from . import parameters as parms
from . import general_methods as gm


def coefficients(age_in_days: int):
    coeffs = dict()
    for k, v in parms.time_limits.items():
        if len(parms.pre_coefficients[k]) != len(parms.time_limits[k]) + 1:
            raise Exception("Coefficient and time-limit mismatch")

        pos = gm.bin_value_to_list(age_in_days, v)
        # print("Type = " + str(k) + ". Days = " + str(age_in_days) + ". Position = " + str(pos))
        coeffs[k] = parms.pre_coefficients[k][pos]
    return coeffs


def _ITS_contribution(value: float, timestring: str):
    age = gm.dtstr_to_age(timestring).days
    TS = 10 + (value - 10)*math.exp(parms.exponents["ITS"]*age)
    return TS


def _general_contribution(keytype: str, values: list, datestrings: list):
    errors = [
        keytype not in parms.time_limits,
        keytype not in parms.exponents,
        keytype not in parms.pre_coefficients,
        keytype not in parms.db_keys.values()
    ]

    if len(values) != len(datestrings):
        raise Exception(
            "Number of dates and values entered do not correspond to one another.")
    if True in errors:
        raise Exception(
            "Key type (" + keytype + ") not recognizes. Errors = " + str(errors))

    contr = 0.0
    for i in range(len(values)):
        age = gm.dtstr_to_age(datestrings[i]).days
        ind_contribution = \
            coefficients(age)[keytype] * values[i] * \
            math.exp(parms.exponents[keytype]*age)
        # Exceptions  
        # misbehaviour always has a negative contribution
        if keytype == "Mbehav":
            ind_contribution = min(ind_contribution, -ind_contribution)
        # Loosing a dispute can have a negative contribution, but winning not.
        if keytype == "Disp":
            ind_contribution = min(ind_contribution, 0)

        contr += ind_contribution
    return contr


def compute_TS(input_info: dict):
    if "ITS" not in input_info:
        raise Exception("Initial Trust Score (ITS) not in input information.")
    if "ZTF" not in input_info:
        raise Exception("Zero Trust Flag not in input information.")

    for key in input_info:
        if key == "user_ID":
            continue
        for sub_key in input_info[key]:
            if type(input_info[key][sub_key]) != list:
                input_info[key][sub_key] = [input_info[key][sub_key]]

    if 1 in input_info["ZTF"]["values"] or '1' in input_info["ZTF"]["values"]:
        return 0.0

    TS = _ITS_contribution(
        input_info["ITS"]["values"][-1], input_info["ITS"]["dates"][-1])

    general_contributors = ["ccITS", "Mturn", "Mab", "Mtxns", "Mbehav", "Disp"]

    for contributer in general_contributors:
        if contributer in input_info:
            values = input_info[contributer]["values"]
            dtstrings = input_info[contributer]["dates"]
            contri = _general_contribution(contributer, values, dtstrings)
            # print("Adding contribution " + str(contri) + " for " + contributer)
            TS += contri

    return max(0.1, min(99.9, TS))
