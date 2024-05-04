from datetime import date 
import os

from vsmetaCodec.vsmetaEncoder import VsMetaMovieEncoder
from vsmetaCodec.vsmetaDecoder import VsMetaDecoder
from vsmetaCodec.vsmetaInfo import VsMetaInfo, VsMetaImageInfo

import glob

def readTemplateFile(filename: str) -> bytes:
    file_content = b'\x00'
    with open(filename, 'rb') as readFile:
        file_content = readFile.read()
        readFile.close()
    return file_content

def process_file(file_path):
    # Define your function to process each file here
    # For example, you can read the file contents or perform any specific task
    # with open(file_path, 'r') as file:
    #     file_contents = file.read()
    #     # Do something with the file contents
    #     print("Processing file:", file_path)
    #     # Example: Print file contents
    #     print(file_contents)

    # --------------------------------------------------------------
    # READER video.mp4.vsmeta
    # --------------------------------------------------------------

    vsmeta_bytes = readTemplateFile(file_path)
    reader = VsMetaDecoder()
    reader.decode(vsmeta_bytes)

    if reader.info.season == 0:
        vsmeta_type = "movie"
    else:
        vsmeta_type = "series"
        if reader.info.tvshowMetaJson == "null":
            reader.info.tvshowMetaJson = ""

    reader.info.printInfo('.')

# Directory where you want to search for .vsmeta files
directory_path = "."

# Search for files with .vsmeta extension in the directory
files = glob.glob(directory_path + "/*.vsmeta")

# Iterate over the files and run the process_file function on each file
for file_path in files:
    print(f"-------------- : Processing file [{file_path}]")
    process_file(file_path)
