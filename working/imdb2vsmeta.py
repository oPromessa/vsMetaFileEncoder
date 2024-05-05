import sys
import os
import shutil

import click

import csv

from datetime import date, datetime
import textwrap

import requests

from imdbmovies import IMDB

from vsmetaCodec.vsmetaEncoder import VsMetaMovieEncoder
from vsmetaCodec.vsmetaDecoder import VsMetaDecoder
from vsmetaCodec.vsmetaInfo import VsMetaInfo, VsMetaImageInfo

def writeVsMetaFile(filename: str, content: bytes):
    with open(filename, 'wb') as writeFile:
        writeFile.write(content)
        writeFile.close()

def readTemplateFile(filename: str) -> bytes:
    # file_content = b'\x00'
    with open(filename, 'rb') as readFile:
        file_content = readFile.read()
        readFile.close()
    return file_content

def lookfor_imdb(movie_title, year=None, tv=None):
    imdb = IMDB()
    results = imdb.search(movie_title, year=year, tv=tv)
    
    # Filter only movie type entries
    movie_results = [result for result in results["results"] if result["type"] == "movie"]
    
    print(f"Found: [{len(movie_results)}] entries for Title: [{movie_title}] Year: [{year}]")

    for cnt, mv in enumerate(movie_results):
        print(f"\tEntry: [{cnt}] Name: [{mv['name']}] Id: [{mv['id']}] Type: [{mv['type']}]")
        
    if movie_results:
        movie_info = imdb.get_by_id(movie_results[0]["id"])
        # print(movie_info)
        return movie_info
    else:
        return None

def search_imdb(movie_title, year):
    imdb = IMDB()
    # year=None, tv=False, 
    result = lookfor_imdb(movie_title, year, tv=False)
    # result = imdb.get_by_name(movie_title, tv=False)
    if result:
        # movie_info = imdb.get_movie(result[0].id)
        return result
    else:
        return None
    
def download_poster(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)

def map_to_vsmeta(imdb_info, posterFile, filename):
    
    # vsmetaMovieEncoder 
    vsmeta_writer = VsMetaMovieEncoder()

    # Build up vsmeta info
    info = vsmeta_writer.info

    # info.showTitle = 
        # 'year': imdb_info['datePublished'],
        # 'Genre': ', '.join(imdb_info['genre']),
        # # 'Director': ', '.join(imdb_info['director']['name']),
        # 'classification': imdb_info['contentRating'],
        # 'rating': imdb_info['rating']['ratingValue'],
        # # Add more fields as needed

    # Title
    info.showTitle = imdb_info['name']
        # Test: ignore
        # info.showTitle2 = imdb_info['name']
    # Short Title
    info.episodeTitle = imdb_info['name']
        # info.year=imdb_info['datePublished'][:4]
    
    # Publishing Date - episodeReleaseDate
    info.setEpisodeDate(date(
        int(imdb_info['datePublished'][:4]),
        int(imdb_info['datePublished'][5:7]),
        int(imdb_info['datePublished'][8:])))
    
    # Set to 0 for Movies: season and episode
    info.season = 0
    info.episode = 0
    
    # Not used. Set to 1900-01-01
    info.tvshowReleaseDate = date(1900, 1, 1)

    # Try with Locked = False
    info.episodeLocked = False

    # Summary
    info.chapterSummary = imdb_info['description']

    # Classification
    # A rating of None would crash the reading of .vsmeta file with error:
    #    return info._readData(info.readSpecialInt()).decode()
    #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8a in position 1: invalid start byte
    info.classification = "" if imdb_info['contentRating'] == None else imdb_info['contentRating']

    # Rating
    info.rating = imdb_info['rating']['ratingValue']

    # Cast
    info.list.cast = [] 
    for actor in imdb_info['actor']:
        info.list.cast.append(actor['name'])
    
    # Genre
    info.list.genre = imdb_info['genre']

    # Director
    info.list.director = []
    for director in imdb_info['director']:
        info.list.director.append(director['name'])

    # Writer    
    info.list.writer = []
    for creator in imdb_info['creator']:
        info.list.writer.append(creator['name'])


    # Read JPG images for Poster and Background
    with open(posterFile, "rb") as image:
        f = image.read()
    
    # Poster (of Movie)
    episode_img = VsMetaImageInfo()
    episode_img.image = f
    info.episodeImageInfo.append(episode_img)

    # Background (of Movie)
    # Use Posters file for Backdrop also
    info.backdropImageInfo.image = f

    # Not used. Set to VsImageIfnfo()
    info.posterImageInfo = episode_img

    # Double check!
    info.timestamp = int(datetime.now().timestamp())

    # Try to set VSMETA to null to force VS to recognize the file???
    # info.episodeMetaJson = ''

    print(f"\tTitle          : {info.showTitle}")
    print(f"\tTitle2         : {info.showTitle2}")
    print(f"\tEpisode title  : {info.episodeTitle}")
    print(f"\tEpisode year   : {info.year}")
    print(f"\tEpisode date   : {info.episodeReleaseDate}")
    print(f"\tEpisode locked : {info.episodeLocked}")
    print(f"\tTimeStamp      : {info.timestamp}")
    print(f"\tClassification : {info.classification}")
    print(f"\tRating         : {0:1.1f}".format(info.rating))
    wrap_text = "\n                 ".join(textwrap.wrap(info.chapterSummary, 150))
    print(f"\tSummary        : {0}".format(wrap_text))
    wrap_text = ("\n                 ".join
                    (textwrap.wrap("".join(["{0}, ".format(name) for name in info.list.cast]), 150)))
    print(f"\tCast           : " + wrap_text)
    wrap_text = ("\n                 ".join
                    (textwrap.wrap("".join(["{0}, ".format(name) for name in info.list.director]), 140)))
    print(f"\tDirector       : " + wrap_text)
    print(f"\tWriter         : " + "".join(["{0}, ".format(name) for name in info.list.writer]))
    print(f"\tGenre          : " + "".join(["{0}, ".format(name) for name in info.list.genre]))

    writeVsMetaFile(filename, vsmeta_writer.encode(info))

    return True

def copy_files_from_csv(csv_file_path, force=False):
    DEST_VOLUME = '/Volumes/video/Movies'

    # Open the CSV file
    with open(csv_file_path, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        
        # Skip the header row
        next(csv_reader)
        
        # Iterate through each row
        for row in csv_reader:
            # Extract the source file path (6th field) and destination folder path (2nd field)
            source_file_path = row[5]  # Assuming the 6th field contains the source file path
            destination_folder_path = os.path.join(DEST_VOLUME, row[1])  # Assuming the 2nd field contains the destination folder path

            print(f"-------------- : Copying title [{row[3].replace('.', ' ').strip()}] year [{row[4]}] filename [{source_file_path}]")
            
            # Check if the source file exists
            if os.path.isfile(source_file_path):
                # Create the destination folder if it doesn't exist
                # os.makedirs(destination_folder_path, exist_ok=True)
                
                # Extract the file name from the source file path
                file_name = os.path.basename(source_file_path)
                
                # Generate the destination file path
                destination_file_path = os.path.join(destination_folder_path, file_name)
                
                # Copy the file to the destination folder if it doesn't exist there
                if not os.path.exists(destination_file_path):
                    shutil.copy(source_file_path, destination_folder_path)
                    print(f"\tCopied ['{file_name}'] to ['{destination_file_path}'].")
                elif not force:
                    click.echo(f"\tSkipping ['{file_name}'] in ['{destination_file_path}']. Destiantion exists. See -f option.")
                else:
                    click.echo(f"\tOverwriting ['{file_name}'] in ['{destination_file_path}'].")
                    shutil.copy(source_file_path, destination_folder_path)
                    print(f"\tCopied ['{file_name}'] to ['{destination_file_path}'].")
            else:
                print(f"\tNot found source file []'{source_file_path}'].")
    print(f"-------------- : File copying process completed.")

@click.command()
@click.argument('file_path', type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('-f', '--force', is_flag=True, help="Force copy if the destination file already exists.")
def main(file_path, force):
    """Process a csv file with Movie Titles (chedk format) and generates .vsmeta and copy to Library."""

    # Load movie titles from CSV
    # CSV File structure
    # Path,Directory Name,Base Name,Filtered Title,Filtered Year
    # [0] = Path,
    # [1] = Directory Name,
    # [2] = Base Name,
    # [3] = Filtered Title,
    # [4] = Filtered Year
    # (added for output) [5] = vsmeta file

    if os.path.isfile(file_path) and file_path.endswith(".csv"):
        click.echo(f"Processing file: [{file_path}].")
    else:
        click.echo("Invalid file path or file format. Please provide a valid path to a .csv file.")
        exit(-1)

    movie_titles = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header_row = next(csv_reader)
        for row in csv_reader:
            try:
                row[4] = int(row[4])
            except ValueError:
                row[4] = None
            movie_titles.append(row)

    with open('movie_vsmeta.csv', 'w', newline='') as outfile:
        # Create a CSV writer object
        csv_writer = csv.writer(outfile)
        header_row.append("vsmeta")
        csv_writer.writerow(header_row)

        for movie in movie_titles:
            filename = movie[2]
            title = movie[3].replace('.', ' ').strip()
            year = movie[4]
            print(f"-------------- : Processing title [{title}] year [{year}] filename [{filename}]")

            # Search IMDB for movie information
            movie_info = search_imdb(title, year=year)
            if movie_info:
                # Download poster
                poster_url = movie_info['poster']
                poster_filename = f'{title.replace(" ", "_")}_poster.jpg'
                download_poster(poster_url, poster_filename)

                # Map IMDB fields to VSMETA
                # and Encode VSMETA
                vsmeta_filename = filename + ".vsmeta"
                map_to_vsmeta(movie_info, poster_filename, vsmeta_filename)
                
                movie[3] = title
                movie.append(vsmeta_filename)
                csv_writer.writerow(movie)
            else:
                print(f"No information found for '{title}'")

    copy_files_from_csv('movie_vsmeta.csv', force)  # Replace 'your_file.csv' with the path to your CSV file

if __name__ == "__main__":
    main()
