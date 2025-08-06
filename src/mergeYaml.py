#!/usr/bin/env python3

import json
import yaml
import argparse
import sys
from utils import load

if __name__ == '__main__':
    '''
    Examples:
    - echo 'HOME=${HOME}' | ./mergeYaml.py => "HOME=/home/...."
    - awk 'FNR==1 && NR!=1 {print "---"}{print}' *.yaml | ./mergeYaml.py -e  => just merge multiple yaml docs into single yaml, without expanding env vars.
    '''

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',     default='/dev/stdin', help='input file path')
    parser.add_argument('-e','--no-expandVars', action='store_false', dest='expandVars', help='flag for expanding environment vars')
    parser.add_argument('-m','--no-merge',      action='store_false', dest='merge',      help='flag to merge multiple docs into one in case of yaml')
    opts = parser.parse_args()
    #print(f'{opts=}', file=sys.stderr)
    #exit(0)

    d = load(path=opts.input, expandVars=opts.expandVars, merge=opts.merge)
    print(yaml.dump(d))
