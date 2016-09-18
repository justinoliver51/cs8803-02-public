"""
Runs on an infinite loop, continuously submitting each piece of a project. If a
failure is found, the log is saved in the requested directory.  This script
must be run from a project directory (e.g. /vagrant/pr1). All JSON logs for
passing tests are automatically removed.

USAGE:
Pass the list of subprojects you want following "--projects" with a comma
delimitter. For example, to test echo and gfserver from project 1:

$ python --projects echo,gfserver --logdir my_fail_dir

The test is stopped when Ctrl-C is typed in the keyboard.
"""
__author__ = "Justin Oliver"
__email__ = "justin.oliver@gatech.edu"

from io import TextIOWrapper
from optparse import OptionParser
import os
from subprocess import check_output
import sys


def call_process(command):
    return check_output(command)


def cmd_parser():
    """
    Parse user's command line and return opts and args.
    """
    projects_help = "Pass subprojects to be tested with a comma delimiter"
    logdir_help = "the directory to store the logs"

    parser = OptionParser()
    parser.add_option("--projects", help=projects_help, default="")
    parser.add_option("--logdir", help=logdir_help, default="pr_failures")
    return parser.parse_args()


def print_results(results, test_num):
    """
    Prints the results of the run.
    """
    print "\n*** RESULTS: ***\n"
    for proj, num_passed in results.iteritems():
        print "{pr}:      {n}/{t}".format(pr=proj, n=num_passed, t=test_num)


def save_results(results, logdir):
    """
    Parses the results, saving the JSON log if there is a failure. If not,
    the log is deleted. Returns 1 if the test passed, 0 otherwise.
    """
    path = results.split('\n')[-2].split("(Details available in ")[1][:-2]
    if results.find("failed") >= 0:
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        if logdir.startswith('/'):
            new_path = logdir + '/' + "/".join(path.split('/')[1:])
        else:
            new_path = os.getcwd() + '/' + logdir + "/".join(path.split('/')[1:])
        path = os.getcwd() + '/' + path
        os.rename(path, new_path)
        return 0
    else:
        os.remove(path)
        return 1

def main():
    opts, args = cmd_parser()
    projects = opts.projects.split(',')
    test_num = 0
    results = {proj:0 for proj in projects}

    try:
        print "Test started... To complete, hit ctrl-c"
        while True:
            for proj in projects:
                command = ["python", "submit.py", proj]
                result = call_process(command)
                results[proj] += save_results(result, opts.logdir)
            test_num += 1
    except KeyboardInterrupt:
        # End of run, print results
        print_results(results, test_num)
        sys.exit(0)


if __name__ == "__main__":
    main()

