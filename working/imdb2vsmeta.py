import csv
import os
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

    # Movie
    info.showTitle = imdb_info['name']
    info.showTitle2 = imdb_info['name']
    info.episodeTitle = imdb_info['name']
    info.year=imdb_info['datePublished'][:4]
    info.setEpisodeDate(date(
        int(imdb_info['datePublished'][:4]),
        int(imdb_info['datePublished'][5:7]),
        int(imdb_info['datePublished'][8:])))
    info.timestamp = int(datetime.now().timestamp())
    info.episodeLocked = True
    info.chapterSummary = imdb_info['description']
    # A rating of None would crash the reading of .vsmeta file with error:
    #    return info._readData(info.readSpecialInt()).decode()
    #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8a in position 1: invalid start byte
    info.classification = "" if imdb_info['contentRating'] == None else imdb_info['contentRating']
    info.rating = imdb_info['rating']['ratingValue']
    info.list.genre = imdb_info["genre"]
    info.list.director = []
    for director in imdb_info["director"]:
        info.list.director.append(director["name"])
    info.list.cast = [] 
    for actor in imdb_info["actor"]:
        info.list.cast.append(actor["name"])
    info.list.writer = []
    for creator in imdb_info["creator"]:
        info.list.writer.append(creator["name"])

    # Poster file
    with open(posterFile, "rb") as image:
        f = image.read()

    # Use Posters file for Backdrop also
    info.backdropImageInfo.image = f

    episode_img = VsMetaImageInfo()
    episode_img.image = f
    info.episodeImageInfo.append(episode_img)

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

def main():
    # Load movie titles from CSV
    movie_titles = []
    movie_year = []
    with open('movie_titles.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            movie_titles.append(row[0])
            try:
                yr = int(row[1])
            except ValueError:
                yr = None
            movie_year.append(yr)

    for idx, title in enumerate(movie_titles):
        print(f"-------------- : Processing title [{title}] year [{movie_year[idx]}]")

        # Search IMDB for movie information
        movie_info = search_imdb(title, year=movie_year[idx])
        if movie_info:
            # Download poster
            poster_url = movie_info['poster']
            poster_filename = f'{title.replace(" ", "_")}_poster.jpg'
            download_poster(poster_url, poster_filename)

            # Map IMDB fields to VSMETA
            # and Encode VSMETA
            vsmeta_filename = f'{title.replace(" ", "_")}.vsmeta'
            map_to_vsmeta(movie_info, poster_filename, vsmeta_filename)
        else:
            print(f"No information found for '{title}'")

if __name__ == "__main__":
    main()
