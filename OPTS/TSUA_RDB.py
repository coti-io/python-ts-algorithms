import sys
import rocksdb
import datetime
import itertools
from . import parameters as parms
from . import general_methods as gm

############################################################
######       Quick methods and non-trivial options       ###
############################################################


class StaticPrefix(rocksdb.interfaces.SliceTransform):
    def __init__(self, uid_length: int):
        self.uid_length = uid_length

    def name(self):
        wrd = "uid_length_" + str(self.uid_length) + "_prefix_extractor"
        return gm.str_to_b(wrd, parms.encoding)

    def transform(self, src):
        return (0, self.uid_length)

    def in_domain(self, src):
        return len(src) >= self.uid_length

    def in_range(self, dst):
        return len(dst) == self.uid_length


def default_db_options(uid_length=parms.uid_length):
    opts = rocksdb.Options()
    opts.create_if_missing = True
    opts.prefix_extractor = StaticPrefix(uid_length)
    opts.max_open_files = 300000
    opts.write_buffer_size = 67108864
    opts.max_write_buffer_number = 3
    opts.target_file_size_base = 67108864

    opts.table_factory = rocksdb.BlockBasedTableFactory(
        filter_policy=rocksdb.BloomFilterPolicy(10),
        block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
        block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))
    return opts


##########################################
#####      Working parts             #####
##########################################


class tsua_rdb:
    '''Note that here the keys are purely the uid's - 
    There is no danger of overwriting the db entry as the userID's should be unique.
    If necessary checks can be put in place to ensure this.  '''

    def __init__(self, dbname: str, options="default"):
        if options == "default":
            options = default_db_options()

        self._db = rocksdb.DB(dbname, options)

    def _get(self, key: str):
        return gm.b_to_str(self._db.get(gm.str_to_b(key, parms.encoding)), parms.encoding)

    def _put(self, key: str, value: str):
        self._db.put(gm.str_to_b(key, parms.encoding),
                     gm.str_to_b(value, parms.encoding))

    def check_if_usr_in_db(self, user_ID: str):
        bytestring = self._db.get(gm.str_to_b(user_ID, parms.encoding))
        return False if bytestring is None else True
    #

    def read_TSUA_parameters(self, user_ID: str):
        if not self.check_if_usr_in_db(user_ID):
            raise Exception("User " + user_ID + " not in DB.")
        divisions = self._get(user_ID).split(parms.major_separator)

        user_stats = dict()
        for major_parm in divisions:
            parameter = None
            for pt in parms.data_types().keys():
                if major_parm.startswith(pt):
                    parameter = pt
            if parameter is None:
                continue

            user_stats[parameter] = dict()
            minor_divisions = major_parm.strip(parameter).strip(
                parms.minor_separator).split(parms.minor_separator)

            key_type = None
            # limits for dates and values sub-keys
            limits = {minor_divisions.index(
                key_type): key_type for key_type in parms.data_types()[parameter]}
            #
            # print("limits for " + str(parameter) + " = " + str(limits))
            for i in range(len(minor_divisions)):
                # what key does this position in the db belong to?
                key_type = limits[i] if i in limits else key_type
                # print("i = " + str(i) + "; key-type = " + str(key_type))
                if key_type is None or minor_divisions[i] == key_type:
                    continue
                val = minor_divisions[i]
                try:
                    val = int(val) if val.isdecimal() else float(val)
                except:
                    pass

                if key_type in user_stats[parameter]:
                    user_stats[parameter][key_type] += [val]
                else:
                    user_stats[parameter][key_type] = [val]

        return user_stats

    #
    def update_db(self, usr_stat_update: dict, overwrite_no_update=False):
        # Safety checks
        if "user_ID" not in usr_stat_update:
            raise Exception(
                "user_ID not in update - update impossible - aborting")
        for major_parm in usr_stat_update:
            # Is it sensible for the ZTF to have dates - consider this at a later stage.
            if major_parm == "user_ID" or major_parm == "ZTF":
                continue
            if "dates" not in usr_stat_update[major_parm]:
                raise Exception('"dates" not in update - this is problem')
            dat = usr_stat_update[major_parm]["dates"]
            try:
                size = 1 if (type(dat) == str or type(dat) ==
                             int or type(dat) == float) else len(dat)
            except Exception as e:
                print("Exception " + str(e) +
                      ", for Parameter: "+str(major_parm))
                raise e
            for min_parm in usr_stat_update[major_parm]:
                type_check = type(usr_stat_update[major_parm][min_parm])
                len_check = 1 if (type_check != list) else len(
                    usr_stat_update[major_parm][min_parm])
                if len_check != size:
                    raise Exception("For paramter " + str(major_parm) + ". Length of values under " + str(min_parm) +
                                    " does not correspond to number of dates (" + str(size) + ") given. Aborting.")

        # Getting the user ID and getting the information from the DB (if appropriate)
        uid = usr_stat_update["user_ID"]
        in_db = self.check_if_usr_in_db(uid)
        prior_data = self.read_TSUA_parameters(uid) if (
            in_db and not overwrite_no_update) else {}
        # Merging and organizing the available data
        data_to_write = self.merge_and_order_data(prior_data, usr_stat_update)

        # Creating the value string for the k, v storage
        output_data_string = ""
        for major_parm in sorted(data_to_write):
            # the user_ID is the key in the k, v storage - no need to add it to the v also
            if major_parm == "user_ID":
                continue

            output_data_string += parms.major_separator + \
                major_parm if len(output_data_string) != 0 else major_parm

            for key_value in sorted(data_to_write[major_parm]):
                output_data_string += parms.minor_separator + key_value
                for value in data_to_write[major_parm][key_value]:
                    output_data_string += parms.minor_separator + str(value)

        # Writing the k, v to the DB
        self._put(usr_stat_update["user_ID"], output_data_string)

    #
    @staticmethod
    def merge_and_order_data(old_data: dict, new_data: dict):
        uid_to_use = None
        # Checking for some serious errors and assigning the uid
        for essent_dat in parms.default_data(datetime.datetime.now().isoformat()):
            if essent_dat not in old_data and essent_dat not in new_data:
                raise Exception("Essential data " +
                                str(essent_dat) + "missing.")

        if "user_ID" not in old_data and "user_ID" not in new_data:
            print('WARNING: "user_ID" not found in either old or new data',
                  file=sys.stderr)
        elif "user_ID" in old_data and "user_ID" in new_data:
            if old_data["user_ID"] == new_data["user_ID"]:
                uid_to_use = new_data["user_ID"]
            else:
                raise Exception('Mismatch between user IDs: old_data["user_ID"] = ' + str(
                    old_data["user_ID"]) + '; new_data["user_ID"] = ' + str(new_data["user_ID"]))
        else:
            uid_to_use = new_data["user_ID"] if "user_ID" in new_data else old_data["user_ID"]

        # Creating an "empty" dictionary in which to merge the old and new data
        merged_data = parms.data_types()
        if uid_to_use is not None:
            merged_data["user_ID"] = uid_to_use

        # Creating safe, empty dictionaries in which insert the given information
        safe_old_data = parms.data_types()
        safe_new_data = parms.data_types()

        # Dummy dictionary to avoid iterating over a changing dictionary
        dat_types = parms.data_types()
        for maj_parm in dat_types:
            if maj_parm == "user_ID":
                continue

            # Converting "old" and "new" data to lists
            for sub_parm in dat_types[maj_parm]:
                if maj_parm in old_data:
                    if sub_parm in old_data[maj_parm]:
                        if type(old_data[maj_parm][sub_parm]) == list:
                            safe_old_data[maj_parm][sub_parm] = old_data[maj_parm][sub_parm]
                        else:
                            safe_old_data[maj_parm][sub_parm] = [
                                old_data[maj_parm][sub_parm]]
                #
                if maj_parm in new_data:
                    if sub_parm in new_data[maj_parm]:
                        if type(new_data[maj_parm][sub_parm]) == list:
                            safe_new_data[maj_parm][sub_parm] = new_data[maj_parm][sub_parm]
                        else:
                            safe_new_data[maj_parm][sub_parm] = [
                                new_data[maj_parm][sub_parm]]

            # Inserting the old data into the dictionary for merged data
            merged_data[maj_parm] = safe_old_data[maj_parm]

            # Inserting the new data into the dictionary while checking for identical dates under the same field
            if "dates" in dat_types[maj_parm]:
                for i in range(len(safe_new_data[maj_parm]["dates"])):
                    test_dt = safe_new_data[maj_parm]["dates"][i]
                    test_val = safe_new_data[maj_parm]["values"][i]

                    # Checking the location of corresponding dates in the "old" and "new" data (if any)
                    corr_dt_index = safe_old_data[maj_parm]["dates"].index(
                        test_dt) if test_dt in safe_old_data[maj_parm]["dates"] else None

                    # Checking the location of corresponding values in the "old" and "new" data (if any)
                    corr_val_index = safe_old_data[maj_parm]["dates"].index(
                        test_dt) if test_dt in safe_old_data[maj_parm]["dates"] else None

                    # Checking if both dates and values correspond (in which case this is interpreted as a duplicate and ignored)
                    if corr_dt_index is not None:
                        if corr_val_index == corr_dt_index:
                            # Notification that duplication detected (and ignored)
                            print("Duplicated dates (" + str(test_dt) + ") and corresponding values (" +
                                  str(test_val) + ") found in the same field (" + str(maj_parm) + ")." +
                                  "This is interpreted as a duplicate - therefore ignoring this value in the new entry.",
                                  file=sys.stderr)
                        else:
                            # If only dates are duplicated a warning is given, but the value is entered (to be considered)
                            merged_data[maj_parm]["dates"] += [test_dt]
                            merged_data[maj_parm]["values"] += [test_val]
                            print("WARNING: Duplicated dates (" + str(test_dt) +
                                  ") found in the same field (" + str(test_val) + "). Problems may occur.", file=sys.stderr)
                    else:
                        # Entering new data if no duplication
                        merged_data[maj_parm]["dates"] += [test_dt]
                        merged_data[maj_parm]["values"] += [test_val]
            else:
                for sub_parm in dat_types[maj_parm]:
                    merged_data[maj_parm][sub_parm] += safe_new_data[maj_parm][sub_parm]

        # ZTF only ever has 1 value - (open for consideration)
        if "ZTF" in new_data:
            merged_data["ZTF"]["values"] = new_data["ZTF"]["values"]
        elif "ZTF" in old_data:
            merged_data["ZTF"]["values"] = old_data["ZTF"]["values"]

        # Sorting the data according to dates (oldest first)
        for major_parm in merged_data:
            sub_dat = merged_data[major_parm]
            if "dates" in sub_dat and type(sub_dat["dates"]) == list:
                sorted_indicies = [sub_dat["dates"].index(
                    x) for x in sorted(sub_dat["dates"])]
                sorted_dates, sorted_values = list(), list()
                for index in sorted_indicies:
                    age = gm.dtstr_to_age(sub_dat["dates"][index])
                    # Remove from DB things which are too old (behavior to be considered)
                    if age.days <= parms.time_limits[major_parm][-1]:
                        sorted_dates.append(sub_dat["dates"][index])
                        sorted_values.append(sub_dat["values"][index])
                merged_data[major_parm]["dates"] = sorted_dates
                merged_data[major_parm]["values"] = sorted_values

        # returning safely merged data
        return merged_data
