Welcome to FP Selector! 
This application chooses the best fluorescent proteins for you to use
based off of spectral overlap, quantum yield, size, and other factors.
It's coded in python and uses the FPBase REST API to get data.

PLAN: 
modules to use: Tkinter, Requests, MatplotLib, 
_
-User picks how many proteins they want
-User picks further critera (qy, price, etc.)
-the program generates the proteins it thinks fit user specifications.
-the program generates links to the papers behind the proteins, and to the 
proteins' graphs on FPBase (ex: https://www.fpbase.org/protein/mazamigreen/).

TODO:
-convert fp_selector.py to OOP
-add functionality for finding 3 compatible proteins
    -will need to figure out how to build algorithm for this
-make GUI with tkinter
    -simulate protein spectra with matplotlib
-add pictures of GUI to README.txt for github viewing