from sys import argv
from os import environ
from pathlib import Path
import re
from typing import List, Dict
from sys import exit
import argparse

import os
from cryptography.hazmat.primitives import serialization

from sql_shell import inputs_fp, outputs_fp
from snowflake_backend import execute_to_csv

parser = argparse.ArgumentParser(description="file conversion to csv")
parser.add_argument("-q", help="source file")
parser.add_argument("-wid", help="workspace id")
#parser.add_argument("-fo", help="file output")

args = parser.parse_args()

if(not args.q):
  workspace_id=args.wid
  input_file = f"input_{workspace_id}.sql"
  with open(f"{inputs_fp}/{input_file}", "r+") as f: 
    query_text:str = f.read() 
else:
  workspace_id=None
  query_text:str = args.q
  print(query_text)

output_file = f"output_{workspace_id}.csv" if workspace_id else "output_1.csv"

execute_to_csv(query=query_text, workspace_id=workspace_id, output_file=f"{outputs_fp}/{output_file}")