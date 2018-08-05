import sys
import datetime
from flask import Flask, request, jsonify, Response, render_template
#
from OPTS import TSUA_RDB
from OPTS import TSUA_calculation
from OPTS import parameters as parms
from OPTS import general_methods as gm
############################################
# parameters for the server and db
############################################
our_host = parms.host
our_port = parms.port
our_DB = TSUA_RDB.tsua_rdb(parms.db_path)
########################################################################
##  Methods for computing the new TS and inserting things into the DB ##
########################################################################


def compute_TS_from_db(user_ID: str):
    in_db = our_DB.check_if_usr_in_db(user_ID)
    if not in_db:
        return "user_ID " + str(user_ID) + ", not found in the DB."

    user_parameters = our_DB.read_TSUA_parameters(user_ID)
    TS = TSUA_calculation.compute_TS(user_parameters)
    return TS


def get_user_info_in_db(user_ID: str):
    in_db = our_DB.check_if_usr_in_db(user_ID)
    if not in_db:
        return "user_ID " + str(user_ID) + ", not found in the DB."

    return our_DB.read_TSUA_parameters(user_ID)


def insert_update_db(user_info: dict, dont_update_overwrite=False):
    if "user_ID" not in user_info:
        return '"user_ID" not included in submitted user information'
    in_db = our_DB.check_if_usr_in_db(user_info["user_ID"])
    word = "overwritten" if (
        in_db and dont_update_overwrite) else "updated" if in_db else "inserted"
    success = False
    try:
        our_DB.update_db(user_info, overwrite_no_update=dont_update_overwrite)
        success = True
    except Exception as e:
        word = str(e) + ". Failed to update db."
        print(word, file=sys.stderr)
    return word if not success else "User " + str(user_info["user_ID"]) + " successfully " + word + " in DB."


def compute_TS_and_update_DB(user_info: dict):
    if "user_ID" not in user_info:
        return 'Error: "user_ID" not included in submitted user information'
    uid = user_info["user_ID"]
    in_db = our_DB.check_if_usr_in_db(uid)

    add_new_ITS = parms.add_new_init_ts

    prior_data = get_user_info_in_db(uid)

    print("Data before merging")
    for key in user_info:
        if key == "user_ID":
            continue
        else:
            print(key + ": ", prior_data[key])

    data_to_compute = our_DB.merge_and_order_data(
        prior_data, user_info) if in_db else user_info

    print("Data after merging")
    for key in user_info:
        if key == "user_ID":
            continue
        else:
            print(key + ": ", data_to_compute[key])

    youngest_ITS_age = gm.dtstr_to_age(
        max(data_to_compute["ITS"]["dates"])).days
    add_new_ITS = add_new_ITS and youngest_ITS_age > parms.youngest_init_ts_max_age

    new_TS = TSUA_calculation.compute_TS(data_to_compute)
    if add_new_ITS:
        data_to_compute["ITS"]["dates"].append(
            datetime.datetime.now().isoformat())
        data_to_compute["ITS"]["values"].append(new_TS)

    successful = insert_update_db(data_to_compute)
    print(successful)
    return new_TS


#########################
##  Running the server ##
#########################
application = Flask(__name__)


@application.route("/TS_from_db", methods=["PUT"])
def ts_from_db():
    uid = request.get_json()["user_ID"]
    result = {"TS": compute_TS_from_db(uid)}
    return jsonify(result)


@application.route("/get_user_info", methods=["PUT"])
def get_user_info():
    uid = request.get_json()["user_ID"]
    # print("user_ID: " + uid)
    result = get_user_info_in_db(uid)
    # print("Result: " + str(result))
    return jsonify(result)


@application.route("/insert_update_user_info", methods=["PUT"])
def insert_update_user_info():
    update_information = request.get_json()
    result = insert_update_db(update_information)
    return jsonify({"Status": result})


@application.route("/overwrite_insert_user_info", methods=["PUT"])
def overwrite_insert_user():
    result = insert_update_db(request.get_json(), dont_update_overwrite=True)
    return jsonify({"Status": result})


@application.route("/compute_TS_update_DB", methods=["PUT"])
def calc_TS_and_update_db():
    information = request.get_json()
    result = compute_TS_and_update_DB(information)
    return jsonify({"TS": result})


@application.route("/uid_in_db", methods=["PUT"])
def check_if_uid_in_db():
    uid = request.get_json()["user_ID"]
    status = "In DB" if our_DB.check_if_usr_in_db(uid) else "Not in DB."
    return jsonify({"user_ID": uid, "Status": status})


if __name__ == '__main__':
    application.run(host=our_host, port=our_port, debug=False)
