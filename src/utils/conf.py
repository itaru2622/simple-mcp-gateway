from typing import Any
import yaml
import json
import sys
import os
from functools import reduce

def load_(path: str='/dev/stdin', encoding: str='utf-8') -> Any:
    """load content into json|yaml|text from file"""

    with open(path, "r", encoding=encoding) as fp:
        c = fp.read()             # read as text
        c = os.path.expandvars(c) # expand environment variables i.e: '${HOME} => /home/user'

        for loader in [ json.loads, yaml.safe_load ]:
        # for each supporting format
            try:
                d = loader(c)
                return d
            except Exception as e:
                continue
        return c

def load(path: str='/dev/stdin', encoding: str='utf-8', expandVars: bool=True, merge: bool=True, removeComment: bool=True) -> Any:
    """load content into json|yaml|text from file

    Args:
      - path (str): file path to load
      - encoding (str): file encoding,
      - expandVars(bool): indicating flag if expand environment vars
      - merge (bool): indicating flag if merging multiple docs when yaml
      - removeComment (bool): indicating flag if remove comment line(startswith #) from json

    Returns:
      Any
    """

    with open(path, "r", encoding=encoding) as fp:
        if removeComment in [True]:
           tmp = fp.readlines()      # read in array
           c = "".join([ l for l in tmp if l.startswith('#')==False ]) # remove comment
        else:
           c = fp.read()             # read as text
        if expandVars:
            c = os.path.expandvars(c) # expand environment variables i.e: '${HOME} => /home/user'

        for loader in [ json.loads, yaml.safe_load_all ]:
        # for each supporting format
            try:
                d = loader(c)
                if loader == yaml.safe_load_all:
                    d = list(d)
                    if d in [None, []]:
                        return None
                    elif len(d) == 1: # single doc => pull up
                        return d[0]
                    #else (multiple docs) => merge dicts
                    if merge and isinstance(d[0], dict):
                       d = mergeDicts(*tuple(d))
                return d
            except Exception as e:
                continue
        return c


def mergeDicts(*dicts: dict) -> dict:
    '''merge multiple dicts into one dict
    cf. https://stackoverflow.com/questions/7204805/deep-merge-dictionaries-of-dictionaries-in-python

    Args:
      - dicts (dict) in va_args style
    Returns:
      dict

    Examples:
        mergeDicts({1:1,2:{1:2}},{1:2,2:{3:1}},{4:4})
        => {1: [1, 2], 2: {1: 2, 3: 1}, 4: 4}
    '''

    if not reduce(lambda x, y: isinstance(y, dict) and x, dicts, True):
        raise TypeError('Object in *dicts not of type dict')
    if len(dicts) < 2:
        raise ValueError('Requires 2 or more dict objects')

    # internal helper function.
    def merge(a, b):
        '''merge two dicts recursively'''
        for k in set(a.keys()).union(b.keys()):
            if k in a and k in b:
                if isinstance(a[k], dict):
                    yield (k, dict(merge(a[k], b[k])))
                else:
                    ret = list({a[k], b[k]})
                    if len(ret) == 1:
                        ret = ret[0]
                    yield (k, sorted(ret))
            elif k in a:
                yield (k, a[k])
            elif k in b:
                yield (k, b[k])
           #else:
           #    raise KeyError(f'something wrong on key {k}')

    # kick helper function, to merge all dicts into one.
    return reduce(lambda x, y: dict(merge(x, y)), dicts[1:], dicts[0])

if __name__ == '__main__':
    '''
    Examples:
    - echo 'HOME=${HOME}' | python3 ./utils.py => "HOME=/home/...."
    - awk 'FNR==1 && NR!=1 {print "---"}{print}' *.yaml | python3 ./utils.py
    '''
    d = load()
    print( json.dumps(d, ensure_ascii=False, indent=2), file=sys.stdout)
