#This file will update the files in the current directory from either Dropbox or Github

import distutils.dir_util as dirUtil
import os
import requests
import tempfile
import zipfile

def updateFromZip(url, destFolder = "", *arg, **kwarg):
  FILE_NAME = "temp.zip"
  
  print("Getting internet data")
  resp = requests.get(url, *arg, **kwarg)
  if resp.status_code != 200:
    return False
    
  print("Creating Folder")
  with tempfile.TemporaryDirectory() as folderName:
    fileName = os.path.join(folderName, FILE_NAME)
    print("Writing file")
    with open(fileName, "wb") as handle:
      handle.write(resp.content)
    print("Unzipping to temp folder")
    with zipfile.ZipFile(os.path.join(folderName, fileName)) as zip:
      zip.extractall(folderName)
    print("Removing zip")
    os.remove(fileName)
    print("Copying files to new directory")
    files = os.listdir(folderName)
    #THIS IS SPECIFIC TO MY IMPLEMENTATION BUT I AM LAZY
    if len(files) == 1: #If we only have the "master" folder
      folderName = os.path.join(folderName, files[0])
    #END SPECIFICITY
    dirUtil.copy_tree(folderName, destFolder)
    print("Done! (deleting temp folder)")
  return True
  
def main():
  from sys import argv
  val = argv[1].lower()
  if val == "git":
    updateFromZip(argv[2])
  elif val == "dropbox":
    updateFromZip(argv[2])
  else:
    print("No valid arguments detected! Should be used like\nupdate git/dropbox urlToGoTo")
    return 1
    
if __name__ == "__main__":
  main()