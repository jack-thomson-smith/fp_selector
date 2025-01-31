import requests
import csv
# import tkinter as tk
from time import sleep

"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
Additional Sources:
https://blog.addgene.org/choosing-your-fluorescent-proteins-for-multi-color-imaging

"""


def refresh_database(field="default_state__em_max", lookup="gte", value="400"):
    """ Searches FPBase database for proteins that match the critera, then
    writes those values to _protein_database.csv. See documentation for list
    of parameters: https://www.fpbase.org/api/. The current default params
    should return all proteins in the database.

    Arguments:
        field: a string of the field you want to look up
               (default: default_state__em_max)
        lookup: a string of the lookup operator you want to use
               (default: gte)
        value: a string of the value you want to find
               (default: 400)"""

    url = "https://www.fpbase.org/api/proteins/"
    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    response_obj = requests.get(url, params=payload)

    print(f"fetch status: {response_obj.status_code} ({response_obj.reason})")

    with open("_protein_database.csv", "w", encoding="utf-8") as csv_file:
        csv_file.write(response_obj.text)

    order_by_brightness(build_protein_list())
    # ^ orders protein list by brightness (bright->dark) & writes info to file


def build_protein_list(file="_protein_database.csv"):
    """ reads csv file and outputs a list of dicts.

    Arguments:
        file: a csv file (default: _protein_database.csv).

    Returns: a list of dicts of protein data. Each dict is a row in
    the file and is mapped to the uuid of the protein."""

    output = []
    with open(file, "r", encoding="utf-8") as csv_file:
        for line in csv.DictReader(csv_file):
            output.append(line)
    return output


def order_by_brightness(protein_list, file="_fp_ordered_brightness.csv"):
    """ Sorts protein list, then writes info in csv format to a file.

    Arguments:
        protein_list: list of dict of proteins
        file: file to write to (default: _fp_ordered_brightness.csv)
    """
    sorted_list = sorted(protein_list,
                         key=lambda x: x["states.0.brightness"],
                         reverse=True)
    # ^ sorts list by brightness, highest -> lowest

    with open(file, "w", newline="", encoding="utf-8") as list_file:
        fieldnames = sorted_list[0].keys()
        writer = csv.DictWriter(list_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(sorted_list)


def build_allowed_spectrum(constraint, radius):
    """function description tbd"""
    constraints_spec = set(range(constraint-(radius), constraint+(radius)+1))
    return set(range(400, 701)) - constraints_spec


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

    output_index = None
    r = 110

    while output_index is None:
        r -= 10  # every loop, decreases radius until a protein is found\
        print("current radius:", r)
        allowed_em_spec = build_allowed_spectrum(constraints["em_max"], r)

        allowed_ex_spec = build_allowed_spectrum(constraints["ex_max"], r)
        order = constraints["order"] + 1
        print("order:", order)
        for index, protein in enumerate(sorted_protein_list):
            allowed_em = int(protein["states.0.em_max"]) in allowed_em_spec
            allowed_ex = int(protein["states.0.ex_max"]) in allowed_ex_spec

            if allowed_em and allowed_ex:
                order -= 1  # every loop, decreases the order until it's 1
                if order == 1:
                    output_index = index

        if r <= 55:  # radius is too low, so protein can't be found w/o overlap
            print("radius is too low...")
            return output_index

    return sorted_protein_list[output_index]


def output_compatible(sorted_protein_list, name, order):
    """function description tbd"""

    p_info = None
    for p in sorted_protein_list:
        if p["name"].casefold() == name.casefold():
            p_info = (int(p["states.0.em_max"]), int(p["states.0.ex_max"]))
    # ^ case-insensitive input mapping to protein
    if p_info is None:
        return "invalid name"

    brightest_p_dict = choose_compatible(sorted_protein_list,
                                         {'em_max': p_info[0],
                                          'ex_max': p_info[1],
                                          'order': order})
    return brightest_p_dict


if __name__ == "__main__":

    ordered_plist = build_protein_list("_fp_ordered_brightness.csv")
    command = ""
    commands = ["list by brightness (lbb)", "pick compatible proteins (pcp)",
                "refresh database (rd)", "list commands (ls)", "exit"]

    print("")
    print("Welcome to FP_Selector!")
    print("")
    print("")
    while command != "exit":
        print("\nPlease enter command:")
        command = input("> ")

        if command == "list by brightest" or command == "lbb":
            for i in range(10):
                print(f"{i+1}: {ordered_plist[i]['name']}")
                sleep(0.05)

        elif command == "pick compatible proteins" or command == "pcp":
            name = input("Please enter protein name below.\n   > ")

            for i in range(10):
                brightest_p = output_compatible(ordered_plist, name, i+1)

                if brightest_p == "invalid name":
                    print("Invalid protein name.")
                    break
                elif brightest_p is None:
                    print("No more proteins can be found.")
                    break

                print(f"{i}: {brightest_p['name']}")
                print(f"    brightness: {brightest_p['states.0.brightness']}")
                print(f"    emission max: {brightest_p['states.0.em_max']}")
                print(f"    excitation max: {brightest_p['states.0.ex_max']}")

        elif command == "refresh database" or command == "rd":
            refresh_database()

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
