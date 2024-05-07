from datetime import date 
import os
import sys

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
    """Read .vsmeta file and print it's contents. 
    
    Images within .vsmeta are saved as image_back_drop.jpg and image_poster_NN.jpg
    When checking multiple files, these files are overwritten.
    """

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

# Check if a file path is provided as a command-line argument
if len(sys.argv) > 1:
    # If a file path is provided, process only that file
    file_path = sys.argv[1]
    if os.path.isfile(file_path) and file_path.endswith(".vsmeta"):
        print("Processing file:", file_path)
        process_file(file_path)
    else:
        print("Invalid file path or file format. Please provide a valid path to a .vsmeta file.")
else:
    # If no file path is provided, search for .vsmeta files in the directory
    # Search for files with .vsmeta extension in the directory
    files = glob.glob(directory_path + "/*.vsmeta")

    # Iterate over the files and run the process_file function on each file
    for file_path in files:
        print(f"-------------- : Processing file [{file_path}]")
        process_file(file_path)
