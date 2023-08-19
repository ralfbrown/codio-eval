#!/bin/bash
# switch to coding problem's subdirectory
cd PyExample

# perform any needed preparation such as compilation
# (no compilation needed for Python)

# run the student's code with the input file the student has prepared
python3 Adder.py <input
exit $?
