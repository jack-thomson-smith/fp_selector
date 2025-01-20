import requests
import csv
# import tkinter as tk
from time import sleep

"""
FPBase API documentation: https://www.fpbase.org/api/
Requests Module documentation: https://requests.readthedocs.io/en/
"""

url = "https://www.fpbase.org/api/proteins/"


def lookup_proteins(field="name", lookup="icontains", value="green"):
    """
    Searches FPBase database for proteins that match the critera. See
    documentation for list of parameters: https://www.fpbase.org/api/

    Arguments:
        field: a string of the field you want to look up (ex: name, seq,
                default_state_qy)
        lookup: a string of the lookup operator you want to use (ex: lt,
                contains)
        value: a string of the value you want to find (ex: green, 541)

    Returns: A response object
    """

    payload = {f"{field}__{lookup}": value}  # "field__lookup":"value"
    return requests.get(url, params=payload)


def create_dictreader(response_object):
    """
    Takes a response object and writes its text to csv_buffer.csv.
    Then, reads that file and outputs a DictReader object.

    Arguments:
        response_object: a response object from the requests module,
        like the one outputted by lookup_protein().

    Returns: a list of dicts of protein data that fit the criteria
    """
    output = []
    with open("csv_buffer.csv", "w") as csv_file:
        csv_file.write(response_object.text)
    with open("csv_buffer.csv", "r") as csv_file:
        for line in csv.DictReader(csv_file):
            output.append(line)
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
    print("___________________________________________________________")
    print("Thanks! Here are the proteins that fit your specifications:\n")

    if field == "" and lookup == "" and value == "":
        protein_list = create_dictreader(lookup_proteins())
    else:
        protein_list = create_dictreader(lookup_proteins(field, lookup, value))

    for i in range(1, len(protein_list)):
        print(f"{i}: {protein_list[i]['name']}")
        sleep(0.05)
    print("")
    print("____________________________________________________________")
    print("Thanks for using FP_Selector!")

    # -------------code above this line-----------------------
    # root.mainloop()
