import tkinter as tk
from tkinter import ttk
# import fp_selector as fp


def showlabel():
    ttk.Label(frm, text="label!").grid(column=1, row=1)


root = tk.Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)


quit_button = ttk.Button(frm,
                         text="Quit",
                         command=root.destroy).grid(column=1,
                                                    row=0)
label_button = ttk.Button(frm,
                          text="Generate label",
                          command=showlabel).grid(column=0,
                                                  row=1)

root.mainloop()
