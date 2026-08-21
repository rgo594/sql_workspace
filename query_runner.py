from sys import argv
from os import environ
from pathlib import Path
import re
from typing import List, Dict
from sys import exit
import argparse

import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization

from sql_shell import inputs_fp, outputs_fp
from snowflake_backend import execute_to_csv

parser = argparse.ArgumentParser(description="file conversion to csv")
parser.add_argument("-q", help="source file")
parser.add_argument("-fi", help="file input")
parser.add_argument("-fo", help="file output")

args = parser.parse_args()

if(not args.q):
  input_file = f"input_{args.fi}.sql"
  with open(f"{inputs_fp}/{input_file}", "r+") as f: 
    query_text:str = f.read() 
else:
  query_text:str = args.q
  print(query_text)

output_file = f"output_{args.fo}.csv" if args.fo else "output_1.csv"

execute_to_csv(query_text, f"{outputs_fp}/{output_file}")