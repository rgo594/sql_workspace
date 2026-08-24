#!/usr/bin/env python3
#might change this using a shell instead

import subprocess
import readline
import atexit
import os
import shlex
from datetime import datetime
import os
from pathlib import Path
import shutil

sql_editor_fp = os.environ["SQL_WORKSPACE_FILEPATH"]
os.makedirs(sql_editor_fp, exist_ok=True)

workspace_fp = f"{sql_editor_fp}/workspace"
os.makedirs(workspace_fp, exist_ok=True)

histfile = os.path.expanduser(f"{sql_editor_fp}/.workspace_history")
Path(histfile).touch(exist_ok=True)

readline.read_history_file(histfile)
atexit.register(readline.write_history_file, histfile)

inputs_fp = f"{workspace_fp}/inputs"
os.makedirs(inputs_fp, exist_ok=True)

outputs_fp = f"{workspace_fp}/outputs"
os.makedirs(outputs_fp, exist_ok=True)

inputs_archive_fp = f"{workspace_fp}/archive/inputs"
os.makedirs(inputs_archive_fp, exist_ok=True)

outputs_archive_fp = f"{workspace_fp}/archive/outputs"
os.makedirs(outputs_archive_fp, exist_ok=True)

def fetch_archive_count(file):
  with open(file, "a+") as f:
    f.seek(0)
    contents = f.read()
    n = int(contents) if contents != "" else 0
    n += 1
    f.seek(0)
    f.truncate()
    f.write(str(n))

  return n

def sp_run(command):
  result = subprocess.run(command, shell=True, text=True, capture_output=True)
  print(result.stdout)
  if result.stderr:
    print("Error:", result.stderr)

def main():
  while True:
    try:
      raw = input("ddb> ")
      parts = shlex.split(raw)
      if not parts:
          continue
      
      command = parts[0]
      args = dict(enumerate(parts[1:]))
      py = "python3"

      if command == "/r":
        execute_input_file: str = (
            f"{py} {sql_editor_fp}/query_runner.py "
            f"-fi {args.get(0, 1)} -fo {args.get(0, 1)}"
        )
        sp_run(execute_input_file)

      elif command == "/cqi":
          input_files = Path(inputs_fp).glob("input_*.sql")

          numbers = [
              int(file.stem.split("_")[-1])
              for file in input_files
          ]

          next_number = max(numbers, default=0) + 1

          print(next_number)
          input_file = Path(inputs_fp) / f"input_{next_number}.sql"
          input_file.touch()

      elif command == "/bq":
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        number = args.get(0, 1)

        input_file = Path(inputs_fp) / f"input_{number}.sql"
        archive_input_file = (
            Path(inputs_archive_fp) / f"archived_input_{number}_{ts}.sql"
        )
        shutil.copy(input_file, archive_input_file)

        output_file = Path(outputs_fp) / f"output_{number}.csv"
        archive_output_file = (
            Path(outputs_archive_fp) / f"archived_output_{number}_{ts}.csv"
        )
        shutil.copy(output_file, archive_output_file)

      elif command == "/bqa":
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        for file in Path(inputs_fp).glob("*.sql"):
            number = file.stem.split("_")[-1]
            archive_file = (
                Path(inputs_archive_fp) / f"archived_input_{number}_{ts}.sql"
            )
            shutil.copy(file, archive_file)

        for file in Path(outputs_fp).glob("*.csv"):
            number = file.stem.split("_")[-1]
            archive_file = (
                Path(outputs_archive_fp) / f"archived_output_{number}_{ts}.csv"
            )
            shutil.copy(file, archive_file)

      elif command == "/dqi":
        input_file = Path(inputs_fp) / f"input_{args.get(0, 1)}.sql"
        input_file.unlink()

      elif command == "/dqo":
        output_file = Path(outputs_fp) / f"output_{args.get(0, 1)}.csv"
        output_file.unlink()

      elif command == "/dqia":
        for file in Path(inputs_fp).glob("*.sql"):
            file.unlink()

      elif command == "/dqoa":
        for file in Path(outputs_fp).glob("*.csv"):
            file.unlink()

      elif command == "/ow":
        sp_run(f"code {sql_editor_fp}/workspace")

      elif command.lower() == "/exit":
        print("Exiting shell...")
        break

      elif command.strip() == "":
        continue

      elif command == "/":
        sp_run(" ".join(parts[1:]))

      else:
        execute_input_file: str = (
            f'{py} {sql_editor_fp}/query_runner.py -q "{raw}"'
        )

        print(execute_input_file)
        sp_run(execute_input_file)
    except KeyboardInterrupt:
      print("\n")
      continue
    except EOFError:
      break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

