import requests
import csv
# import tkinter as tk
from time import sleep

"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
"""

PWD = 50  # protein wavelength distribution


def lookup_proteins(field="name", lookup="icontains", value="green"):
    """ Searches FPBase database for proteins that match the critera, and
    outputs a response object. See documentation for list of parameters:
    https://www.fpbase.org/api/

    Arguments:
        field: a string of the field you want to look up (ex: name, seq,
                default_state_qy)
        lookup: a string of the lookup operator you want to use (ex: lt,
                contains)
        value: a string of the value you want to find (ex: green, 541)

    Returns: A response object """

    url = "https://www.fpbase.org/api/proteins/"
    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    response_object = requests.get(url, params=payload)
    print(f"status: {response_object.status_code} ({response_object.reason})")

    return response_object


def create_protein_dict(response_object):
    """ Takes a response object and writes its text to csv_buffer.csv.
    Then, reads that file and outputs a dict mapped to each protein's
    uuid (unique 4-digit number) containing a dict of the protein's data.
    This could probably be done without writing to a file.

    Arguments:
        response_object: a response object from the requests module,
        like the one outputted by lookup_protein().

    Returns: a dict of dicts of protein data that fit the criteria """

    output = {}
    with open("csv_buffer.csv", "w") as csv_file:
        csv_file.write(response_object.text)
    with open("csv_buffer.csv", "r") as csv_file:
        for line in csv.DictReader(csv_file):
            output[line["uuid"]] = line
    return output


def prompt_choose_compatible(protein_list):
    """ gets user input to choose compatible proteins.
    """

    protein_data = maximize_for_brightness(protein_list)
    usable_spec = set(range(400, 701))
    usable_spec -= set(range(protein_data[0]-PWD, protein_data[0]+PWD))
    # now, usable_spec is a set of all wavelengths between 400 and 700
    # that the protein we just found's em max does not overlap with.

    protein_list2 = create_protein_dict(lookup_proteins(field="",
                                                        lookup="",
                                                        value=""
    ))



def maximize_for_brightness(protein_list):
    """ Given dict of protein dicts, chooses brightest one, and
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
    print("Please input your specifications below.")
    print("")
    field = input("protein field: ")
    lookup = input("lookup operator: ")
    value = input("value of lookup: ")
    print("\nfetching data....")

    if field == "" and lookup == "" and value == "":
        protein_list = create_protein_dict(lookup_proteins())
    else:
        protein_list = create_protein_dict(lookup_proteins(field,
                                                           lookup,
                                                           value))

    print("\nPlease enter command:")
    command = ""
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
            prompt_choose_compatible(protein_list)
        elif command == "else":
            pass  # loop breaks due to command now being "exit"
        else:
            print("unknown")
    print("")
    print("_______")
    print("Thanks for using FP_Selector!")
