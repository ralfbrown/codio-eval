# Codio-Eval - An enhanced test-case based student-program evaluation for Codio.com

This project provides eval.py, an evaluation script which provides an approximate equivalent of Codio's built-in Standard Code Test assessment, but with finer-grained control.

The enhancements over Codio's Standard Code Test are:
- per-testcase points
- per-testcase time limits
- per-testcase control over whether to show difference between expected and actual output
- per-testcase control over whether to show input if the output is incorrect
- parallel evaluation if the test case is small enough

The per-testcase control permits a single Run button in the Guide to
process both sample and hidden test cases, while parallel evaluation
reduces the wait for results when test cases take multiple seconds
each to execute.

# Setup

To use codio-eval, you will need to
- copy the evaluation script `eval.py` into `.guides/secure`
- create input and expected-output files for each test case in an appriopriate subdirectory of `.guides/secure`
- create or adapt a bash script to invoke eval.py with appropriate arguments (samples for Java, Python, and JavaScript [nodejs] are included)
- create an Advanced Code Test assessment which invokes the wrapper bash script

## Copy Evaluation Script

All files in this repository are already in the correct subdirectory for a Codio workspace, so one approach is to download the Github-generated tarball and simple extract it in your assignment's workspace.  Or you can manually copy `.guides/secure/eval.py` in this repo to the same subdirectory in your assignment.

## Create Input/Output Files

For each test case, you will need to create two files - an input file and an expected output file.  You may optionally create a third file containing feedback text, which will be displayed if the actual output differs from the expected output.

The input files are specified in the invocation of eval.py.  The script finds the corresponding output file for each input by replacing "in" in the file's base name by "out".  Feedback files are similarly found by first attempting to replace "input" by "feedback" and then just "in" by feedback.

It is highly recommended that all of the testcase files and the wrapper script (next section) for a particular coding problem be placed in a problem-specific subdirectory of `.guides/secure/`.

## Create/Adapt Wrapper Script

The wrapper script is used to perform any pre-execution tasks such as compiling the student's submission or restoring any files the student should *not* change, and then invoke eval.py to perform the actual program runs and comparison of actual output against expected output.


## Create Advanced Code Test Assessment

