import requests
import csv
# import tkinter as tk
from time import sleep

"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
"""


def lookup_proteins(field="name", lookup="icontains", value="green"):
    """
    Searches FPBase database for proteins that match the critera, and
    oututs a response object. See documentation for list of parameters: 
    https://www.fpbase.org/api/

    Arguments:
        field: a string of the field you want to look up (ex: name, seq,
                default_state_qy)
        lookup: a string of the lookup operator you want to use (ex: lt,
                contains)
        value: a string of the value you want to find (ex: green, 541)

    Returns: A response object
    """
    url = "https://www.fpbase.org/api/proteins/"
    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    response_object = requests.get(url, params=payload)
    print(f"status: {response_object.status_code} ({response_object.reason})")

    return response_object


def create_protein_dict(response_object):
    """
    Takes a response object and writes its text to csv_buffer.csv.
    Then, reads that file and outputs a dict mapped to each protein's
    uuid (unique 4-digit number) containing a dict of the protein's data.
    This could probably be done without writing to a file.

    Arguments:
        response_object: a response object from the requests module,
        like the one outputted by lookup_protein().

    Returns: a dict of dicts of protein data that fit the criteria
    """
    output = {}
    with open("csv_buffer.csv", "w") as csv_file:
        csv_file.write(response_object.text)
    with open("csv_buffer.csv", "r") as csv_file:
        for line in csv.DictReader(csv_file):
            output[line["uuid"]] = line
    return output


if __name__ == "__main__":
    # root = tk.Tk(screenName="FP_Selector",
    #             baseName="Fluorescent Protein Selector",
    #             className="FP_Selector (Tkinter)", useTk=1)
    # -------------code below this line-----------------------

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
        elif command == "else":
            pass  # loop breaks due to command now being "exit"
        else:
            print("unknown")
    print("")
    print("_______")
    print("Thanks for using FP_Selector!")

    # -------------code above this line-----------------------
    # root.mainloop()
