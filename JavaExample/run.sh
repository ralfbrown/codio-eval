#!/bin/bash
# switch to coding problem's subdirectory
cd JavaExample

# perform any needed preparation such as compilation
javac Adder.java

# run the student's code with the input file the student has prepared
java Adder <input
exit $?
