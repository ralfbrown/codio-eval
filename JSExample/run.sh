#!/bin/bash
# switch to coding problem's subdirectory
cd JSExample

# perform any needed preparation such as compilation
# (no compilation needed for JavaScript/nodejs)

# run the student's code with the input file the student has prepared
node Adder.js <input
exit $?
