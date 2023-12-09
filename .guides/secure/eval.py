#!/usr/bin/env python3
## Copyright (c) 2022,2023 Carnegie Mellon University
## LastEdit: Ralf Brown 09dec2023

import os
import sys
import resource
import subprocess
import time
import difflib   # https://docs.python.org/3/library/difflib.html
from concurrent.futures import ThreadPoolExecutor

### configuration
USE_V1 = 1	     ## use send_partial instead of send_partial_v2?
USE_HTML = 1
SHOW_INPUT = 0	     ## display (beginning of) input file on incorrect output
SHOW_DIFF = 0        ## 1 to show output's difference from expected, 0 to hide
SHOW_HTML_DIFF = 0   ## set to 0 for plaintext unified diff
DEFAULT_POINTS = 1

MAX_LINES = 15	     ## maximum number of lines to diff on incorrect program output

### Codio auto-grading support functions
CODIO_RUNNING = False
sys.path.append('/usr/share/codio/assessments')
try:
    from lib.grade import send_partial, send_partial_v2, FORMAT_V2_MD, FORMAT_V2_HTML, FORMAT_V2_TXT
    CODIO_RUNNING = 'CODIO_PARTIAL_POINTS_V2_URL' in os.environ
except:
    pass
### end 

CODIO_RUNNING = True

def is_float(f):
    try:
        f = int(f)
        return True
    except:
        return False

def to_float(s):
    try:
        return float(s)
    except:
        return 0.0

def is_int(i):
    try:
        i = int(i)
        return True
    except:
        return False

def decorate(s, before, after):
    if USE_HTML:
        return before + s + after
    else:
        return s

def limit_length(s):
    if len(s) > 511:
        return s[:505] + "..."
    else:
        return s

def feedback_file(infilename):
    if 'input' in infilename:
        fbname = infilename.replace('input','feedback')
        if os.path.exists(fbname):
            return fbname
    elif 'in' in infilename:
        fbname = infilename.replace('in','fb')
        if os.path.exists(fbname):
            return fbname
    return None

def compare_output(out, ref):
    if ref != None and len(ref) != len(out):
        return False
    for o,r in zip(out, ref):
        if o != r:
            return False
    return True

def colorize_diff(line):
    if line and CODIO_RUNNING:
        if USE_HTML:
            line = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        if line[0] == '-':
            return decorate(line,f"<span style='color:#701818;background:#FFE0E0'>","</span>")
        elif line[0] == '+':
            return decorate(line,f"<span style='color:#107010;background:#E0FFE0'>","</span>")
    return line

def put_in_text_box(text):
    if USE_HTML:
        return "<div style='width: 95%; white-space: nowrap; overflow-x: auto; border: 2px solid blue; padding: 2px 2px;'>" + \
            text + "</div>"
    else:
        return text

def show_difference(out, ref, trunc = False):
    if SHOW_HTML_DIFF:
        differ = difflib.HtmlDiff()
        return differ.make_table(out,ref,"Output","Expected")
    else:
        differ = difflib.Differ()
        brk = "<br/>" if USE_HTML else "\n"
        to_box = brk.join(colorize_diff(l) for l in differ.compare(out,ref) if l and l[0] != '?')
        if trunc:
            to_box = to_box + brk + "...output truncated..."
        return colorize_diff("- Output ") + " / Both / " + colorize_diff("+ Expected ") + "\n" \
            + put_in_text_box(to_box)

def run_prog(result_text,points,timeout,prog,infile,reffile,show_diff,show_input):
    time_limit = max(1.1*timeout, timeout + 0.25)
    elapsed = -9.99
    OK = False
    with open(infile,'r') as input:
        timed_out = False
        try:
            start_time = time.time()
            result = subprocess.run(prog,timeout=time_limit,stdin=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            elapsed = time.time() - start_time
        except subprocess.TimeoutExpired as e:
            result_text += decorate(f"timeout ({e.timeout}s)","<span style='color:red'>","</span>")
            result_text = decorate(result_text,"<B>","</B>")
        except Exception as e:
            print(e)
            result_text = str(e)
        else:
            if result.returncode != 0:
                before = "<span style='color:red'>"
                after = "</span>"
                stderr_text = result.stderr.decode('utf-8')
                if "ivision" in stderr_text or "ivide by" in stderr_text:
                    errtype = "DivideError"
                elif "emory" in stderr_text:
                    errtype = "MemoryError"
                elif "stack" in stderr_text or "verflow" in stderr_text or "RecursionError" in stderr_text:
                    errtype = "StackError"
                elif "Null" in stderr_text or "null" in stderr_text or "NoneType" in stderr_text:
                    errtype = "NullPtr"
                elif ".regex." in stderr_text or "Regex " in stderr_text:
                    errtype = "RegexError"
                elif "ut of range" in stderr_text or "OutOfBounds" in stderr_text:
                    errtype = "IndexError"
                elif "ArithmeticExc" in stderr_text:
                    errtype = "MathError"
                elif "IOException" in stderr_text:
                    errtype = "IOError"
                elif "NumberFormatExc" in stderr_text:
                    errtype = "BadNumber"
                elif "IllegalArg" in stderr_text:
                    errtype = "ArgError"
                elif "FileNotFound" in stderr_text:
                    errtype = "FileNotFound"
                elif "NoSuchElement" in stderr_text:
                    errtype = "IterateErr"
                elif "TypeError" in stderr_text:
                    errtype = "TypeError"
                elif "AttributeError" in stderr_text:
                    errtype = "AttribErr"
                elif "NameError" in stderr_text:
                    errtype = "NameError"
                elif "KeyError:" in stderr_text:
                    errtype = "KeyError"
                else:
                    errtype = f"RunError {result.returncode}"
                result_text += decorate(errtype,before,after) + f" in {round(elapsed,2)}s"
                result_text = decorate(result_text,"<B>","</B>")
                if show_input:
                    stdout_text = result.stdout.decode('utf-8')
                    if stdout_text:
                        outtext = limit_length(stdout_text)
                        result_text += decorate(outtext,"<br/><pre>","</pre>\n")
                if show_diff:
                    errtext = limit_length(stderr_text)
                    result_text += decorate(errtext,"<br/><pre>","</pre>\n")
            elif reffile != infile:
                outtext = result.stdout.decode('utf-8').split('\n')
                if len(outtext) > 1 and outtext[-1] == '':
                    outtext = outtext[:-1]
                reftext = None
                try:
                    with open(reffile,'r') as ref:
                        reftext = ref.read().split('\n')
                        if len(reftext) > 1 and reftext[-1] == '':
                            reftext = reftext[:-1]
                except:
                    reftext = [ f"{{ Error reading reference output from {reffile} }}" ]
                OK = compare_output(outtext,reftext)
                if not OK:
                    before = "<span style='color:red'>"
                    res_type = f"FAILED at {round(elapsed,2)}s"
                elif elapsed <= timeout:
                    before = "<span style='color:green'>"
                    res_type = f"passed in {round(elapsed,2)}s"
                else:
                    before = "<span style='color:orange'>"
                    res_type = f"overtime at {round(elapsed,2)}s"
                result_text += decorate(res_type,before,"</span>")
                result_text = decorate(result_text,"<B>","</B>")
                feedback = feedback_file(infile)
                fbtext = ""
                have_output = False
                if not OK and feedback is not None:
                    try:
                        with open(feedback,'r') as fb:
                            fbtext = fb.read().split('\n')
                            if len(fbtext) > 1 and fbtext[-1] == '':
                                fbtext = fbtext[:-1]
                    except:
                        pass
                    if fbtext:
                        brk = "<br/>" if USE_HTML else "\n"
                        result_text = result_text + "\n" + put_in_text_box(brk.join(fbtext))
                        have_output = True
                if not OK and show_input:
                    intext = None
                    try:
                        with open(infile,'r') as inf:
                            intext = limit_length(inf.read()).split('\n')
                            if len(intext) > 1 and intext[-1] == '':
                                intext = intext[:-1]
                    except:
                        pass
                    if intext:
                        brk = "<br/>" if USE_HTML else "\n"
                        ellipsis = brk+"..." if len(intext) > 10 else ""
                        if not have_output:
                            result_text += "\n"
                        result_text += "Input:\n" + put_in_text_box(brk.join(intext[:10]) + ellipsis)
                        have_output = True
                if not OK and show_diff:
                    if reftext:
                        before = "" if SHOW_HTML_DIFF else "\n" if not have_output else ""
                        after = "" if SHOW_HTML_DIFF else ""
                        truncated = max(len(outtext),len(reftext)) > MAX_LINES
                        result_text = (result_text + before
                                       + show_difference(outtext[:MAX_LINES],reftext[:MAX_LINES],truncated)
                                       + after)
                    else:
                        result_text = result_text + '\n' + '\n'.join(outtext[:MAX_LINES])
                        if len(outtext) > MAX_LINES:
                            result_text += '...\n'
            else:
                result_text += result.stdout.decode('utf-8')
    return result_text, OK, elapsed

def run_testcase(testnum:int, prog, infile:str, curr_pts, timeout:float, show_diff, show_input):
    reffile = infile.replace('input','output')
    result_text, success, elapsed \
        = run_prog(f"Check {testnum} ",curr_pts,timeout,prog,infile,reffile,show_diff,show_input)
    earned_pts = 0
    if success and elapsed >= 0:
        if elapsed <= timeout:
            earned_pts = curr_pts
        else:
            result_text2, success2, elapsed2 = run_prog(f"retry {testnum} ",
                                                        curr_pts,timeout,prog,infile,reffile,show_diff,show_input)
            result_text3, success3, elapsed3 = run_prog(f"retry {testnum} ",
                                                        curr_pts,timeout,prog,infile,reffile,show_diff,show_input)
            result_text = result_text + '\n' + result_text2 + '\n' + result_text3
            if success2 and success3 and 0.0 <= elapsed2 <= timeout and 0.0 <= elapsed3 <= timeout:
                result_text += f"\n(Check {testnum} full marks)"
                earned_pts = curr_pts
            elif success2 and success3 and ((0.0 <= elapsed2 <= timeout) or (0.0 <= elapsed3 <= timeout)):
                result_text += f"\n(Check {testnum} 75% credit)"
                earned_pts = (0.75 * curr_pts)
            elif (success2 and 0.0 <= elapsed2 <= timeout) or (success3 and 0.0 <= elapsed3<= timeout):
                result_text += f"\n(Check {testnum} 50% credit)"
                earned_pts = (0.5 * curr_pts)
            elif success2 and success3:
                result_text += f"\n(Check {testnum} 25% credit)"
                earned_pts = (0.25 * curr_pts)
            else:
                result_text += f"\n(Check {testnum} too slow)"
    return result_text, earned_pts

def run_all_testcases(num_procs:int, timeout:float, prog, infile_list:list):
    total_pts = 0
    correct_pts = 0
    global DEFAULT_POINTS
    curr_pts = DEFAULT_POINTS
    curr_dir = ''
    global SHOW_DIFF, SHOW_INPUT
    show_diff = SHOW_DIFF
    show_input = SHOW_INPUT
    with ThreadPoolExecutor(max_workers = num_procs) as executor:
        testnum = 1
        futures = []
        for infile in infile_list:
            if infile and infile[0] == '-':
                if infile[1:] == '-d':
                    show_diff = 1
                elif infile[1:] == '-i':
                    show_input = 1
                elif infile[1:] == '-q':
                    show_diff = 0
                    show_input = 0
                elif infile[1:4] == '-t=' and is_float(infile[4:]):
                    timeout = to_float(infile[4:])
                elif is_int(infile[1:]):
                    curr_pts = int(infile[1:])
                elif '/' in infile:
                    curr_dir = infile[1:]
                    if curr_dir[-1] != '/':
                        curr_dir += '/'
                continue
            if not '/' in infile:
                infile = curr_dir + infile
            futures.append(executor.submit(run_testcase, testnum, prog, infile, curr_pts, timeout, show_diff, show_input))
            total_pts += curr_pts
            testnum += 1
        overall_result_text = ''
        for future in futures:
            result_text, earned = future.result()
            correct_pts += earned
            if overall_result_text and overall_result_text[-1] != '\n' and not overall_result_text.endswith('div>'):
                overall_result_text += "\n"
            overall_result_text += result_text
    return correct_pts, total_pts, overall_result_text
    
argv0 = "{prog}"

def usage():
    diff_type = "HTML" if SHOW_HTML_DIFF else "text"
    print(f"Usage: {argv0} {{flags}} timeout execstring infile [infile ...]")
    print(f"flags:")
    print(f"\t-D\tshow difference between expected and actual output")
    print(f"\t-d\ttoggle showing/hiding diffs")
    print(f"\t-q\tquiet mode, don't show diff between expected and actual")
    print(f"\t-t\ttoggle HTML/text diff (default {diff_type})")
    print(f"\t-pN,M\trun N processes in parallel, with M megabytes of memory each")
    print(f"'infile' may start with '-' for special options:")
    print(f"\tif followed by a number, set point value for following input files")
    print(f"\tif followed by pathname including '/', set current dir for files")
    print(f"\tif followed by a second '-', set processing options:")
    print(f"\t\t--d\tshow diff between output and expected")
    print(f"\t\t--i\tshow input file on incorrect output")
    print(f"\t\t--q\tdo not show input or diff when incorrect")
    print(f"\t\t--t=N\tupdate timeout to N seconds")
    exit(2)

def main():
    global SHOW_INPUT, SHOW_DIFF, SHOW_HTML_DIFF, USE_HTML, argv0
    argv0 = sys.argv[0]
    num_procs = 1
    while len(sys.argv) > 1 and sys.argv[1][0] == '-':
        if sys.argv[1] == '-d':
            SHOW_DIFF = 1 - SHOW_DIFF
        elif sys.argv[1] == '-D':
            SHOW_DIFF = 1
        elif sys.argv[1] == '-t':
            SHOW_HTML_DIFF = 1 - SHOW_HTML_DIFF
        elif sys.argv[1] == '-q':
            SHOW_DIFF = 0
        elif sys.argv[1] == '-H':
            USE_HTML = 0
        elif sys.argv[1][:2] == '-p':
            parms = sys.argv[1][2:].split(',')
            if len(parms) < 2:
                sys.argv = []
                break
            num_procs = int(parms[0])
            if num_procs < 1:
                num_procs = 1
            mem_limit = int(parms[1])
            if mem_limit < 16 * num_procs:
                mem_limit = 16 * num_procs
        sys.argv = sys.argv[1:]
    if len(sys.argv) < 3:
        usage()
        exit(2)
    timeout = to_float(sys.argv[1])
    prog = sys.argv[2]
    if '|' in prog:
        prog = prog.replace('"','').split('|')
    infile_list = sys.argv[3:]
    if num_procs > 1:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (mem_limit*1024*1024, hard))
    correct_pts, total_pts, overall_result_text = run_all_testcases(num_procs, timeout, prog, infile_list)
#    grade = 0.0 if correct_pts == 0 else 100.0 * ((correct_pts + 0.01) / total_pts)
    grade = correct_pts
    if CODIO_RUNNING:
        earned = decorate(f"{correct_pts}/{total_pts}","<b>","</b>")
        feedback = 'Points earned: ' + earned + '\n' + overall_result_text
        if USE_V1:
            if not USE_HTML:
                print("</pre>") # break out of preformatted text in Guide box
            print(feedback)
            try:
                send_partial(grade)
                res = True
            except NameError as e:
                print(f'\nUnable to send grade to Codio')
                exit(USE_HTML)  # return 0 if user test run rather than scoring run
        else:
            res = send_partial_v2(grade, feedback, format=FORMAT_V2_HTML)
        if not res or grade <= 0:
            exit(1)
    else:
        print(grade)
        print(overall_result_text)
    exit(0)

if __name__ == '__main__':
    main()
