#!/bin/bash
# switch to the subdirectory of the workspace in which the student's code is stored
cd Adder
# in here, you can copy any files from .guides/secure over top of the files in the
# student code directory if you wish to prevent students from modifying any files
# containing harness code or the like; this is more secure (though less flexible)
# than annotating unalterable sections with FREEZE CODE BEGIn / FREEZE CODE END
# when students have access to the terminal window.

# specify the base name of the main program file and the per-testcase timeout in seconds
PROGNAME=Adder
TIMEOUT=1

# specify the subdirectory of .guides/secure containing test cases and
# the per-testcase points to award
PROGDIR=adder
POINTS=10

# The command to compile the student's submission.  Abort the evaluation on error.
javac ${PROGNAME}.java || exit 1

# Finally, the command to run and score the submission.
# This example assignment (read two integers, add them, and print the
# sum) needs essentially no additional memory beyond that required by
# the Java VM, so we can use all four cores in a standard box and
# split up the 768 MB of memory (less a small overhead).  The Java VM
# needs about 2GB virtual address space to start up, so that is the
# memory limit we set on invoking Java.  To prevent one runaway
# testcase from crashing others running in parallel through lack of
# memory, we also need to explicitly limit the heap space Java will
# use, which we do in the arguments passed to 'java'.  The limit for 1
# process is ~650MB, for 2 about 320MB, for 3 about 220MB, and for 4
# about 160MB.
python3 ../.guides/secure/eval.py -p4,2000 ${TIMEOUT} "java|-Xms120M|-Xmx160M|${PROGNAME}" \
	-${POINTS} -../.guides/secure/${progdir}/ \
	--d --i input001.txt \
	--q --d input002.txt \
	--q input003.txt
exit $?

# in the above invocation, input001.txt will be given as input and the
# program's output will be compared against output001.txt.  If the
# output is incorrect, the actual and expected outputs are shown (--d)
# as well as the input the program was given (--i).

# For input002.txt, we first disable both --d and --i with the --q,
# then turn on --d again, so that output differences are shown but the
# input remains hidden.  Finally, for input003.txt, we only show
# whether or not the program produced the expected output.
