import string
import random
import datetime
import requests
from OPTS import TSUA_calculation
from OPTS import parameters as parms
from OPTS import general_methods as gm

##################################
# Helper methods for testing
##################################
test_max_age = 360  # days


def easy_request(command: str):
    return "http://" + str(parms.host) + ":" + str(parms.port) + "/" + command


def easy_put(command: str, data):
    return requests.put(easy_request(command), json=data).json()


def generate_random_uid(length: int):
    choices = string.ascii_letters + string.digits
    uid = ""
    for i in range(length):
        uid += random.choice(choices)
    return uid
####################################################
# Methods to generate user information for testing
####################################################


def generate_test_dict_no_uid(forced_values=None):
    now_dt = datetime.datetime.now()
    two_years_ago = (now_dt - datetime.timedelta(days=730.5)).isoformat()
    eight_months_ago = (
        now_dt - datetime.timedelta(days=8.0*365.25/12.0)).isoformat()

    dates = list()
    for i in range(12):
        time_d = random.random() * test_max_age
        dates.append((datetime.datetime.now() -
                      datetime.timedelta(days=time_d)).isoformat())

    dates.sort()
    # print(dates)
    output_dict = parms.data_types()
    output_dict["ZTF"]["values"] = [0]
    output_dict["ITS"]["values"], output_dict["ITS"]["dates"] = [
        50], [eight_months_ago]

    i = 0
    for datestr in dates:
        i += 1
        #
        output_dict["Mturn"]["values"] += [(0.1 + 0.9*random.random()) * 500]
        output_dict["Mturn"]["dates"] += [datestr]
        #
        output_dict["Mab"]["values"] += [(0.3 + 0.7*random.random()) * 2500]
        output_dict["Mab"]["dates"] += [datestr]
        #
        output_dict["Mtxns"]["values"] += [random.randint(0, 60)]
        output_dict["Mtxns"]["dates"] += [datestr]
        #
        if i % 3 == 0:
            output_dict["ccITS"]["values"] += [random.choice([0, 1])]
            output_dict["ccITS"]["dates"] += [datestr]
            #
            output_dict["Mbehav"]["values"] += [random.choice([1, 2, 5])]
            output_dict["Mbehav"]["dates"] += [datestr]
            #
            output_dict["Disp"]["values"] += [
                random.choice([0, -2, -1, 0, 1, 2])]
            output_dict["Disp"]["dates"] += [datestr]

    if forced_values is not None:
        for key in forced_values:
            output_dict[key] = forced_values[key]

    return output_dict


def generate_test_dict_with_uid(forced_values=None):
    forced_values = dict() if forced_values is None else forced_values
    forced_values.update({"user_ID": generate_random_uid(parms.uid_length)})
    user_info = generate_test_dict_no_uid(forced_values=forced_values)
    return user_info


############################################
# Actually testing the calls to the server
############################################
num_test_users = 75

# Generating the information
print("Testing ITSA server.")
all_user_input_info = dict()
for i in range(num_test_users):
    test_user = generate_test_dict_with_uid()
    all_user_input_info[test_user["user_ID"]] = test_user


##########################################################
# Checking adding and retrieving information from the DB
# I.e. checks /insert_update_user_info
# checks /get_user_info
##########################################################
print("\n Checking calculating the TS from the DB")

for user in all_user_input_info:
    response = easy_put("insert_update_user_info", all_user_input_info[user])
    print("Inserting user in DB was " + str(response))

for user in all_user_input_info:
    from_db = easy_put("get_user_info", {"user_ID": user})
    for major_field in all_user_input_info[user]:
        if major_field not in from_db:
            # print(str(major_field) + " not in DB. From input = " + str(all_user_input_info[user][major_field]))
            continue
        else:
            for minor_field in all_user_input_info[user][major_field]:
                if all_user_input_info[user][major_field][minor_field] != from_db[major_field][minor_field]:
                    print("From input: ")
                    print(all_user_input_info[user][major_field][minor_field])
                    print("From datab: ")
                    print(from_db[major_field][minor_field])

##########################################################
# Checking calculating the TS from the DB
# I.e. checks /TS_from_db
##########################################################
print("\n Checking calculating the TS from the DB")
for user in all_user_input_info:
    tss_from_db = easy_put("TS_from_db", {"user_ID": user})
    print("TS for " + str(user) + " = " + str(tss_from_db))

update_and_modify_choices = [random.choice(
    list(all_user_input_info)) for i in range(4)]
update_and_modify_choices = list(set(update_and_modify_choices))
update_and_modify_choices = update_and_modify_choices[:25]

mod_dates = list()
for i in range(5):
    dtstr = (datetime.datetime.now() -
             datetime.timedelta(days=(4-i))).isoformat()
    mod_dates.append(dtstr)

##########################################################
# Checking modifying the DB at a later time
# I.e. checks /compute_TS_update_DB and /get_user_info
##########################################################
print("\n\n Checking modifying the DB at a later time \n")
for later_modification in update_and_modify_choices:
    mods = {"Mbehav": {"dates": [], "values": []}}
    mods["Mbehav"]["dates"] = mod_dates
    mods["Mbehav"]["values"] = [5 for i in range(len(mod_dates))]
    mods["user_ID"] = later_modification
    new_TS = easy_put("compute_TS_update_DB", mods)
    print("New TS for " + later_modification + " = " + str(new_TS))

# Checking user info input against database this time we should differences from the modifications
for user in all_user_input_info:
    from_db = easy_put("get_user_info", {"user_ID": user})

    for major_field in all_user_input_info[user]:
        if major_field not in from_db:
            # print(str(major_field) + " not in DB. From input = " + str(all_user_input_info[user][major_field]))
            continue
        else:
            for minor_field in all_user_input_info[user][major_field]:
                if all_user_input_info[user][major_field][minor_field] != from_db[major_field][minor_field]:
                    print("\nChecking field: " + major_field +
                          ", and subfield: " + str(minor_field) + ", for user " + user)

                    print(
                        "from INPUT = " + str(all_user_input_info[user][major_field][minor_field]))
                    print("from DB = " +
                          str(from_db[major_field][minor_field]))

#######################################
# Checking if overwriting works:
# I.e. checks /ovwerwrite_insert_user_info
########################################
print("\n\n Checking if overwriting works \n")
overwrite_checks = list(all_user_input_info)
random.shuffle(overwrite_checks)
overwrite_checks = overwrite_checks[:5]

for uid in overwrite_checks:
    before_from_db = easy_put("get_user_info", {"user_ID": uid})
    overwrite_dict = generate_test_dict_no_uid({"user_ID": uid})
    test_result = easy_put("overwrite_insert_user_info", overwrite_dict)
    print("Overwriting was " + str(test_result))
    after_from_db = easy_put("get_user_info", {"user_ID": uid})

    for maj_parm in before_from_db:
        for sub_parm in before_from_db[maj_parm]:
            print("\nChecking field: " + maj_parm +
                  ", and subfield: " + str(sub_parm) + ", for user " + uid)

            print("Before = " + str(before_from_db[maj_parm][sub_parm]))
            print("After = " + str(after_from_db[maj_parm][sub_parm]))


print("\n" + str(all_user_input_info.keys()))
