import math

db_path = "./DBs"
encoding = "utf-8"
uid_length = 5
major_separator = ";"
minor_separator = ","
host = "0.0.0.0"
port = "8050"
##
youngest_init_ts_max_age = 365
add_new_init_ts = True

# An explanation of what the various keys represent
db_keys = {
    "Zero Trust Flag": "ZTF",
    "Initial Trust Score": "ITS",
    "Initial Trust Score Change Counters": "ccITS",
    #
    "Monthly turnover": "Mturn",
    "Monthly average balance": "Mab",
    "Monthly transactions": "Mtxns",
    "Misbehavior": "Mbehav",
    "Dispute outcome": "Disp"
}

# Generates an empty dictionary to be used as a datastructure


def data_types():
    data_types = {
        "ZTF": {"values": []},
        "ITS": {"values": [], "dates": []},
        "ccITS": {"values": [], "dates": []},
        #
        "Mturn": {"values": [], "dates": []},
        "Mab": {"values": [], "dates": []},
        "Mtxns": {"values": [], "dates": []},
        "Mbehav": {"values": [], "dates": []},
        "Disp": {"values": [], "dates": []}
    }
    return data_types


def default_data(datetimestring: str):
    default_data_types = {
        "ZTF": {"dates": datetimestring, "values": 1},
        "ITS": {"dates": datetimestring, "values": 0},
    }
    return default_data_types



# i.e. These values are desiged to decay to half the value in half a year.
#
# Unclear values
# ITS: current implementation is the user gets a new ITS if the latest value is more than 1 year old (for consideration)
# ccITS: how long should these influence the TS?
# Mbehav: Perhaps this should depend on the severity of the incident
# Disp: Perhaps this should depend on the severity of the incident
# clear
# ZTF: never decays - it must be manually changed
exponents = {
    "ITS": - 2 * math.log(2) * 1/365.25,
    "ccITS": - 2 * math.log(2) * 1/365.25,
    "Mbehav": - 2 * math.log(2) * 1/365.25,
    "Disp": - 2 * math.log(2) * 1/365.25,
    #
    "Mturn": - 2 * math.log(2) * 1/365.25,
    "Mab": - 2 * math.log(2) * 1/365.25,
    "Mtxns": - 2 * math.log(2) * 1/365.25,
    "ZTF": 0
}


# Contains the various timeout values - The last value is the amount of time a value stays in the DB
# Before the 0th entry the coefficient has a specific value. Between the 0 and 1 entry the coefficient has another entry. After the 1st entry the value falls out of the db.
# ZTF, ITS, in the dB for 10 years,
# ccITS value changes after 5 years and stays in DB for 10 years
# all other values change after 1/2 years and stay in DB fo 1 year
time_limits = {
    "ZTF": [-1, 3652.5],
    "ITS": [-1, 3652.5],
    "ccITS": [3652.5/2.0, 3652.5],
    #
    "Mturn": [365.25/2.0, 365.25],
    "Mab": [365.25/2.0, 365.25],
    "Mtxns": [365.25/2.0, 365.25],
    "Mbehav": [365.25/2.0, 365.25],
    "Disp": [365.25/2.0, 365.25]
}


# The possible coefficient choices corresponding to the time ranges.
# Note also that there must be 1 more coefficient than timestages
# Note that the coefficients are meaningless for "ZTF" and "ITS" - they are not used at all.
#
# Disp: Negative values indicate losses, positive wins. Magnitude is the severity - only losses influence TS.
pre_coefficients = {
    "ZTF": [1.0, 1.0, 1.0],
    "ITS": [1.0, 1.0, 1.0],
    "ccITS": [-4, -2.0, 0.0],
    #
    "Mturn": [0.01, 0.005, 0.000],
    "Mab": [0.005, 0.003, 0.000],
    "Mtxns": [0.1, 0.05, 0.000],
    "Mbehav": [-1.0, -0.5, 0.0],
    "Disp": [2.0, 1.0, 0.0]
}
