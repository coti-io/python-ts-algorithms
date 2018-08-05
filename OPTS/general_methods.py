import datetime
import dateutil.parser

def b_to_str(byte_in: bytes, encoding: str):
    return "" if byte_in is None else byte_in.decode(encoding=encoding)


def str_to_b(str_in: str, encoding: str):
    return str_in.encode(encoding=encoding)


def dtstr_to_age(timestring: str):
    t2 = datetime.datetime.now()
    t1 = dateutil.parser.parse(str(timestring))
    return (t2 - t1)


def bin_value_to_list(value: float, in_list: list):
    '''Marks the value as 0 if it is less than the lowest value in the list, 1 if it is between values 0 and 1 ... etc.
    Note that this means the output goes (inclusively) from 0 to len(in_list) . Note also should be sorted on input. '''
    sorted_list = sorted(in_list)
    if sorted_list != in_list:
        raise Warning(
            "The input list was not sorted. Sorting and carrying on.")

    for i in range(len(sorted_list)):
        if i == 0 and value < sorted_list[i]:
            break
        elif sorted_list[i-1] <= value < sorted_list[i]:
            break
        elif value >= sorted_list[-1]:
            return len(sorted_list)
        else:
            continue

    if i == len(sorted_list):
        raise Exception("Something went wrong.")

    return i

