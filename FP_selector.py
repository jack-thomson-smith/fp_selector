import requests
import csv
import operator as o
# import tkinter as tk
from time import sleep

"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
"""

PWD = 50  # protein wavelength distribution


def refresh_database(field="default_state__em_max", lookup="gte", value="400"):
    """ Searches FPBase database for proteins that match the critera, then
    writes those values to _protein_database.csv. See documentation for list
    of parameters: https://www.fpbase.org/api/. The current default params
    should return all proteins in the database.

    Arguments:
        field: a string of the field you want to look up (ex: name, seq,
                default_state_qy)
        lookup: a string of the lookup operator you want to use (ex: lt,
                contains)
        value: a string of the value you want to find (ex: green, 541)"""

    url = "https://www.fpbase.org/api/proteins/"
    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    response_object = requests.get(url, params=payload)
    print(f"status: {response_object.status_code} ({response_object.reason})")
    with open("_protein_database.csv", "w") as csv_file:
        csv_file.write(response_object.text)
        #  writes refreshed data to file

    order_by_brightness(create_protein_list)


def create_protein_list(file="_protein_database.csv"):
    """ reads _protein_database.csv and outputs a list of dicts.

    Arguments:
        file: a csv file (like _protein_database.csv).

    Returns: a list of dicts of protein data. Each dict is a row in
    the file and is mapped to the uuid of the protein."""

    output = []
    with open(file, "r") as csv_file:
        for line in csv.DictReader(csv_file):
            output.append(line)
    return output


def order_by_brightness(protein_list, file="_fp_ordered_brightness.csv"):
    """ WIP! need to develop sorting algorithm to rank proteins by brightness,
    then write that info to file.

    """
    sorted_list = sorted(protein_list,
                         key=lambda x: x["states.0.brightness"],
                         reverse=True)
    # ^ sorts list by brightness, highest -> lowest

    with open(file, "w", newline='') as list_file:
        fieldnames = sorted_list[0].keys()
        writer = csv.DictWriter(list_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(sorted_list)


def maximize_for_brightness(protein_list):
    """ Given list of protein dicts, chooses brightest one, and
    returns its emission max, excitation max, brightness value, and uuid.
    Could make this function more efficient by not accessing pdict values
    for every increment of brightness, and instead only accessing it once
    the loop has found the brightest one. Might do that someday!

    Arguments:
        protein_list: dict of dicts from create_protein_dict()
    Returns: (em max of protein, ex max, brightness value, uuid) """

    output = (0, 0, 0, None)  # (em_max, ex_max, brightness, uuid)
    for pdict in protein_list.values():
        if output[2] < pdict["states.0.brightness"]:

            output = (pdict["states.0.em_max"],
                      pdict["states.0.ex_max"],
                      pdict["states.0.brightness"],
                      pdict["uuid"])
    return output


if __name__ == "__main__":
    print("")
    print("Welcome to FP_Selector!")
    print("")

    command = ""
    print("\nPlease enter command:")
    while command != "exit":
        command = input("> ")
        if command == "list dict":
            for (key, value) in protein_list.items():
                print(f"{key}: {value}\n\n")
        elif command == "list names":
            count = 1
            for protein in protein_list.values():
                print(f"{count}: {protein['name']}")
                count += 1
                sleep(0.01)
        elif command == "pick compatible proteins" or command == "pcp":
            num = input("how many?\n> ")
            if num == 2:
                prompt_choose_compatible(protein_list)
            else:
                print("functionality has not been added.")
        elif command == "refresh database":
            refresh_database()
        elif command == "else":
            pass  # loop breaks due to command now being "exit"
        else:
            print("unknown")
    print("")
    print("_______")
    print("Thanks for using FP_Selector!")
