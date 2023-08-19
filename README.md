# Codio-Eval - An enhanced test-case based student-program evaluation for Codio.com

This project provides eval.py, an evaluation script which provides an approximate equivalent of Codio's built-in Standard Code Test assessment, but with finer-grained control.

The enhancements over Codio's Standard Code Test are:
- per-testcase points
- per-testcase time limits, with partial credit if just at/above the time limit
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

The wrapper script is used to perform any pre-execution tasks such as compiling the student's submission or restoring any files the student should *not* change, and then invoke eval.py to perform the actual program runs and comparison of actual output against expected output.  See .guides/*_example/eval.sh for sample wrapper scripts.

## Create Advanced Code Test Assessment

To run the test cases you have set up above, you will need to add one or more Advanced Code Test assessments to the guide page for the coding problem.

Configure each assessment as follows:

- "General" tab: name and instructions as desired

- "Execution" tab:

-- Language = Custom

-- Command = "bash .guides/secure/{SUBDIR}/eval.sh"

-- Timeout = 3 * sum of per-testcase timeouts or higher (the script re-runs a test case twice if it takes between 100% and 110% of the specified time limit)

- "Grading" tab: **Enable** "Allow Partial Points".  Set points, options, and rationale as desired.

- "Parameters" tab: normally left blank

- "Metadata" tab: fill out as usual

- "Files" tab: be sure to include .guides/secure/eval.py, .guides/secure/{SUBDIR}/*, as well as "run.sh" and "input" in the problem's subdirectory under the workspace top-level directory (if using the optional Run or Debug options detailed below).

## Optional: Run on Custom Input

Create a file named "input" in the subdirectory containing the code files to be edited by the student, and fill it with whatever default value is appropriate (such as the first example input described in the instructions).  Add an invocation like
```
{Run with custom input}(bash {subdir}/run.sh)
```
to the guide.

## Optional: Configure Debugger

In the menu Tools|Debugger Settings, create a new entry named e.g. Example, and set it to run the student's code with file "{subdir}/input".  Then add
```
{Debug with custom input|debugger}(Example)
```
to the guide.

## Optional: Code Visualizer

If the code for the problem is in a supported language, can be set up such that it can be run without input (some examples follow), and is sufficiently small (fewer than about 300 program steps), you can add a button to run the student's code under the visualizer.  Add
```
[Code Visualizer](open_tutor {subdir}/MainFile.ext)
```
to the guide.

