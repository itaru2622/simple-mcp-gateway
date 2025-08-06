
from typing import Any
import yaml
import json
import sys
import os

def load(path: str='/dev/stdin', encoding: str='utf-8') -> Any:
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
