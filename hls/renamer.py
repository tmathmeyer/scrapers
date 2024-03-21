
import os
import re


JOBDIR = re.compile("Job........-....-....-....-............-.........-(.*)")


def RenameJobsInDirectory(directory:str):
  for entry in os.listdir(directory):
    if match := JOBDIR.match(entry):
      print(match.group(1))


RenameJobsInDirectory('./content')