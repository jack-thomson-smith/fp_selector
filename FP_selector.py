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

TODO:
-convert fp_selector.py to OOP (maybe later)
-add functionality for finding 3 compatible proteins
    -will need to figure out how to build algorithm for this
-make GUI with tkinter
    -simulate protein spectra with matplotlib
-add pictures of GUI to README.txt for github viewing

"""


def refresh_database(field="default_state__em_max", lookup="gte", value="380"):
    """Searches FPBase database for proteins that match the critera, writes
    those values to _protein_database.csv, then sorts the .csv file by protein
    brightness and writes the sorted list to _fp_ordered_brightness.csv.
    See documentation for list of parameters: https://www.fpbase.org/api/.
    The current default params should return all proteins in the database."""
    url = "https://www.fpbase.org/api/proteins/"
    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    response_obj = requests.get(url, params=payload)
    print(f"fetch status: {response_obj.status_code} ({response_obj.reason})")

    with open("_protein_database.csv", "w", encoding="utf-8") as csv_file:
        csv_file.write(response_obj.text)

    order_by_brightness(build_protein_list())
    # ^ orders protein list by brightness (bright->dark) & writes info to file


def build_protein_list(file="_protein_database.csv"):
    """Reads the given .csv file and outputs a list of dicts."""
    output = []
    with open(file, "r", encoding="utf-8") as csv_file:
        for line in csv.DictReader(csv_file):
            output.append(line)
    return output


def order_by_brightness(protein_list, file="_fp_ordered_brightness.csv"):
    """Sorts protein list, then writes the csv info to the passed file. """
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


def build_allowed_spectrum(maxes, radius):
    """Builds the allowed wavelength spectrum for a fluorescent protein to be
    compatible with, with the given constraints. """
    unallowed_spec = set()  # idk if unallowed is a word
    allowed_spec = set(range(380, 701))
    for max in maxes:
        unallowed_spec |= set(range(max-(radius), max+(radius)+1))
        allowed_spec -= unallowed_spec
    return allowed_spec


def has_empty_values(protein_dict):
    """Checks if the given protein dict has empty values for the brightness,
    emission max, or excitation max. If it does, returns True, if it doesn't,
    returns False. """
    if protein_dict["states.0.brightness"] == '':
        return True
    elif protein_dict["states.0.em_max"] == '':
        return True
    elif protein_dict["states.0.ex_max"] == '':
        return True
    else:
        return False


def choose_compatible(sorted_protein_list, constraints):
    """Chooses compatible proteins based off of constraints parameter.
    The idea is to find the brightest proteins that have both em_maxes
    and ex_maxes that are at least 55-70 nm seperated. Returns None if
    no protein was found.

    constraints: dict in the format {"em_maxes": list,
                                     "ex_maxes": list,
                                     "order": int}
    "order" denotes which protein will be chosen. If it's 1, then the first
    protein that matches the criteria will be chosen. If it's 2, then the
    second protein that matches the criteria will be chosen, and so on."""
    compatible_protein_index = None
    r = 70

    while compatible_protein_index is None:
        r -= 5  # every loop, decreases radius until a protein is found
        allowed_em_spec = build_allowed_spectrum(constraints["em_maxes"], r)
        allowed_ex_spec = build_allowed_spectrum(constraints["ex_maxes"], r)
        order = constraints["order"]

        for index, protein in enumerate(sorted_protein_list):
            em_allowed = int(protein["states.0.em_max"]) in allowed_em_spec
            ex_allowed = int(protein["states.0.ex_max"]) in allowed_ex_spec

            if em_allowed and ex_allowed:
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


def calc_bscore(proteins):
    score = 0
    for p in proteins:
        score += float(p["states.0.brightness"])
    return score


def output_compatible(sorted_protein_list, name, order, amount):
    """Matches user inputted protein name to a protein dict in the protein
    list, then returns brightest protein dict(s) that are compatible w/ it."""
    pd = validate_protein_from_name(sorted_protein_list, name)
    if pd is None:
        return None
    # bpd_1 means brightest protein dict #1
    bpd_1 = choose_compatible(sorted_protein_list,
                              {'em_maxes': [int(pd["states.0.em_max"])],
                               'ex_maxes': [int(pd["states.0.ex_max"])],
                               'order': order})
    if amount == 1:  # only finds the brightest compat. protein and returns it
        return bpd_1

    # ______Below this comment is code for finding more than 1 compat. protein
    bpd_2 = choose_compatible(sorted_protein_list,
                              {'em_maxes': [int(pd["states.0.em_max"]),
                                            int(bpd_1["states.0.em_max"])],
                               'ex_maxes': [int(pd["states.0.ex_max"]),
                                            int(bpd_1["states.0.ex_max"])],
                               'order': order})
    brightest_combo = [pd, bpd_1, bpd_2]
    score = calc_bscore(brightest_combo)

    for i in range(100):

        bpd_1 = choose_compatible(sorted_protein_list,
                                  {'em_maxes': [int(pd["states.0.em_max"])],
                                   'ex_maxes': [int(pd["states.0.ex_max"])],
                                   'order': order+i+1})  # order+=1 every loop
        bpd_2 = choose_compatible(sorted_protein_list,
                                  {'em_maxes': [int(pd["states.0.em_max"]),
                                                int(bpd_1["states.0.em_max"])],
                                   'ex_maxes': [int(pd["states.0.ex_max"]),
                                                int(bpd_1["states.0.ex_max"])],
                                   'order': order})
        print("\ncurrent iteration bscore:", calc_bscore([pd, bpd_1, bpd_2]))
        print(f"   (testing {bpd_1['name']} and {bpd_2['name']})")
        if calc_bscore([pd, bpd_1, bpd_2]) > score:
            score = calc_bscore([pd, bpd_1, bpd_2])
            brightest_combo = [pd, bpd_1, bpd_2]

    print("brightest score: ", score)
    return brightest_combo


def get_protein_info_string(protein_dict):
    """Given a protein dict (from protein_list), returns relevant information
    in a string."""
    underlined_name = "\033[4m" + protein_dict['name'] + "\033[0m"
    ex_max = int(protein_dict['states.0.ex_max'])
    em_max = int(protein_dict['states.0.em_max'])

    output_string = f""" {underlined_name}
    brightness: {protein_dict['states.0.brightness']}
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
            amount = int(input("How many?\n   >"))
            if amount == 1:
                for i in range(5):
                    # bp means brightest protein
                    bp = output_compatible(sorted_protein_list=ordered_plist,
                                           name=name,
                                           order=i+1,
                                           amount=1)
                    if bp is not None:  # e.g. no compatible found
                        print(f"{i+1}:{get_protein_info_string(bp)}\n")
                    sleep(0.05)

            elif amount == 2:
                bp_combo = output_compatible(sorted_protein_list=ordered_plist,
                                             name=name,
                                             order=1,
                                             amount=2)
                for p in bp_combo:
                    print(p["name"])

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

        elif command == "ln":
            total1 = 0
            total2 = 0
            total3 = 0
            for pd in ordered_plist:
                wl = int(pd["states.0.em_max"])
                if wl <= 640:
                    total1 += 1
                if wl >= 440:
                    total2 += 1
                if wl >= 640 and wl >= 440:
                    total3 += 1
            print(total1 * (total2) * (total3))

        else:
            if command != "exit":
                print("unknown")

    print("")
    print("_______")
    print("Thanks for using FP_Selector!")
