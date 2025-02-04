import requests
import csv
import os
from time import sleep
# import tkinter as tk

os.system("")  # this makes underlining work


"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
Additional Sources:
https://blog.addgene.org/choosing-your-fluorescent-proteins-for-multi-color-imaging

"""


def refresh_database(field="default_state__em_max", lookup="gte", value="380"):
    """Searches FPBase database for proteins that match the critera, then
    writes those values to _protein_database.csv. See documentation for list
    of parameters: https://www.fpbase.org/api/. The current default params
    should return all proteins in the database.

    Arguments:
        field: a string of the field you want to look up
               (default: default_state__em_max)
        lookup: a string of the lookup operator you want to use
               (default: gte)
        value: a string of the value you want to find
               (default: 380)"""

    url = "https://www.fpbase.org/api/proteins/"
    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    response_obj = requests.get(url, params=payload)

    print(f"fetch status: {response_obj.status_code} ({response_obj.reason})")

    with open("_protein_database.csv", "w", encoding="utf-8") as csv_file:
        csv_file.write(response_obj.text)

    order_by_brightness(build_protein_list())
    # ^ orders protein list by brightness (bright->dark) & writes info to file


def build_protein_list(file="_protein_database.csv"):
    """Reads the given .csv file and outputs a list of dicts.

    Arguments:
        file: a csv file (default: _protein_database.csv).

    Returns: a list of dicts of protein data."""

    output = []
    with open(file, "r", encoding="utf-8") as csv_file:
        for line in csv.DictReader(csv_file):
            output.append(line)
    return output


def order_by_brightness(protein_list, file="_fp_ordered_brightness.csv"):
    """Sorts protein list, then writes info in csv format to a file.

    Arguments:
        protein_list: list of dict of proteins
        file: file to write to (default: _fp_ordered_brightness.csv)
    """
    sorted_list = [p for p in protein_list if not has_empty_values(p)]
    # ^ removes proteins with no brightness/ex/em value

    sorted_list = sorted(sorted_list,
                         key=lambda x: float(x["states.0.brightness"]),
                         reverse=True)
    # ^ sorts list by brightness, highest -> lowest
    # the float() is very important!!! otherwise it is a string!!

    with open(file, "w", newline="", encoding="utf-8") as list_file:
        fieldnames = sorted_list[0].keys()
        writer = csv.DictWriter(list_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_list)


def build_allowed_spectrum(constraint, radius):
    """Builds the allowed wavelength spectrum for a fluorescent protein to be
    compatible with, with the given constraints. """
    constraints_spec = set(range(constraint-(radius), constraint+(radius)+1))
    return set(range(380, 701)) - constraints_spec


def has_empty_values(pdict):
    """Checks if the given protein dict has empty values for the brightness,
    emission max, or excitation max. If it does, returns True, if it doesn't,
    returns False. """
    if pdict["states.0.brightness"] == '':
        return True
    elif pdict["states.0.em_max"] == '':
        return True
    elif pdict["states.0.ex_max"] == '':
        return True
    else:
        return False


def choose_compatible(sorted_protein_list, constraints):
    """Chooses compatible proteins based off of constraints parameter.
    The idea is to find the brightest proteins that have both em_maxes
    and ex_maxes that are at least 60-100 nm seperated.

    Arguments:
        sorted_protein_list: list of proteins (presorted by brightness).
        constraints: dict in the format {"em_max": int,
                                         "ex_max": int,
                                         "order": int}
                    "order" denotes which protein will be chosen. If it's
                    1, then the first protein that matches the criteria
                    will be chosen. If it's 2, then the second protein that
                    matches the criteria will be chosen, and so on.

    Returns: protein dict, or None if no protein was found."""
    compatible_protein_index = None
    r = 70

    while compatible_protein_index is None:
        r -= 5  # every loop, decreases radius until a protein is found
        allowed_em_spec = build_allowed_spectrum(constraints["em_max"], r)
        allowed_ex_spec = build_allowed_spectrum(constraints["ex_max"], r)
        order = constraints["order"]

        for index, protein in enumerate(sorted_protein_list):
            allowed_em = int(protein["states.0.em_max"]) in allowed_em_spec
            allowed_ex = int(protein["states.0.ex_max"]) in allowed_ex_spec

            if allowed_em and allowed_ex:
                if order == 1:
                    compatible_protein_index = index
                order -= 1  # decreases the order by 1 every loop

        if r <= 55:  # radius is too low, so protein can't be found w/o overlap
            print("No further compatible proteins were found.")
            return None

    return sorted_protein_list[compatible_protein_index]


def validate_protein_from_name(protein_list, inputted_name):
    """Input validation for user name input. Returns the name of the
    protein from the input, or None if the protein doesn't exist."""
    output = None
    for protein_dict in protein_list:
        if protein_dict["name"].casefold() == inputted_name.casefold():
            output = protein_dict
    # ^ case-insensitive input mapping to protein
    if output is None:
        print("Unable to validate protein identity.")
    return output


def output_compatible(sorted_protein_list, name, order):
    """Matches user inputted protein name to a protein dict in the protein
    list, then returns the brightest protein dict that is compatible w/ it."""
    pd = validate_protein_from_name(sorted_protein_list, name)
    # pd means protein dict
    if pd is None:
        return None

    brightest_p_dict = choose_compatible(sorted_protein_list,
                                         {'em_max': int(pd["states.0.em_max"]),
                                          'ex_max': int(pd["states.0.ex_max"]),
                                          'order': order})
    return brightest_p_dict


def get_protein_info_string(pdict):
    """Given a protein dict (from protein_list), returns relevant information
    in a string."""
    underlined_name = "\033[4m" + pdict['name'] + "\033[0m"
    ex_max = int(pdict['states.0.ex_max'])
    em_max = int(pdict['states.0.em_max'])

    output_string = f""" {underlined_name}
    brightness: {pdict['states.0.brightness']}
    ex/em max: {ex_max}/{em_max}"""

    return output_string


if __name__ == "__main__":
    ordered_plist = build_protein_list("_fp_ordered_brightness.csv")
    command = ""
    commands = ["list by brightness (lbb)", "pick compatible proteins (pcp)",
                "refresh database (rd)", "list commands (ls)", "get info (gi)",
                "exit"]

    print("")
    print("Welcome to FP_Selector!")
    print("")
    print("")
    while command != "exit":
        print("\nPlease enter command:")
        command = input("> ")

        if command == "list by brightest" or command == "lbb":
            for i in range(5):
                print(f"{i+1}: {get_protein_info_string(ordered_plist[i])}\n")
                sleep(0.05)

        elif command == "pick compatible proteins" or command == "pcp":
            name = input("Please enter protein name below.\n   > ")

            for i in range(5):
                brightest_p = output_compatible(ordered_plist, name, i+1)
                if brightest_p is not None:  # e.g. no compatible found
                    print(f"{i+1}:{get_protein_info_string(brightest_p)}\n")
                sleep(0.05)

        elif command == "refresh database" or command == "rd":
            refresh_database()

        elif command == "get info" or command == "gi":
            name = input("Enter protein:\n   >")
            protein_dict = validate_protein_from_name(ordered_plist, name)
            if protein_dict is not None:  # (unable to find protein)
                print("\n" + get_protein_info_string(protein_dict))

        elif command == "list commands" or command == "ls":
            print("commands:")
            for c in commands:
                print(" ", c)

        else:
            if command != "exit":
                print("unknown")

    print("")
    print("_______")
    print("Thanks for using FP_Selector!")
