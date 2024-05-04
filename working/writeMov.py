from datetime import date 
import os

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

writer = VsMetaMovieEncoder()

# Movie
info = writer.info
info.showTitle = 'Dune: Part One'
info.showTitle2 = 'Dune: Part One'
info.episodeTitle = 'Dune: Part One'
info.year="2021"
# info.episodeReleaseDate = date(2021, 10, 21)
info.setEpisodeDate(date(2021, 10, 21))
info.timestamp = 1492209544
info.episodeLocked = True
info.chapterSummary = 'A noble family becomes embroiled in a war for control over the galaxy\'s most valuable asset while its heir becomes troubled by visions of a dark future.'
info.classification = '12A'
info.rating = 8.0
# info.list.cast[]
# info.list.director[]
# info.list.writer[]
info.list.genre.append('Action')
info.list.genre.append('Adventure')
info.list.genre.append('Drama')

with open("dune.jpg", "rb") as image:
  f = image.read()

info.backdropImageInfo.image = f

episode_img = VsMetaImageInfo()
episode_img.image = f
info.episodeImageInfo.append(episode_img)

# execute, prepare result
# test_data = writer.encode(info)

# compare
# template = readTemplateFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "template_movie1.vsmeta"))

writeVsMetaFile(os.path.join(os.path.realpath(os.curdir),'video.mp4.vsmeta'), writer.encode(info))

# --------------------------------------------------------------
# READER 100m.vsmeta
# --------------------------------------------------------------

# vsmeta_bytes = readTemplateFile(os.path.join(os.path.realpath(os.curdir),"100m.vsmeta"))
# reader = VsMetaDecoder()
# reader.decode(vsmeta_bytes)

# if reader.info.season == 0:
#     vsmeta_type = "movie"
# else:
#     vsmeta_type = "series"
#     if reader.info.tvshowMetaJson == "null":
#         reader.info.tvshowMetaJson = ""

# reader.info.printInfo('.')


# --------------------------------------------------------------
# READER video.mp4.vsmeta
# --------------------------------------------------------------

vsmeta_bytes = readTemplateFile(os.path.join(os.path.realpath(os.curdir),"video.mp4.vsmeta"))
reader = VsMetaDecoder()
reader.decode(vsmeta_bytes)

if reader.info.season == 0:
    vsmeta_type = "movie"
else:
    vsmeta_type = "series"
    if reader.info.tvshowMetaJson == "null":
        reader.info.tvshowMetaJson = ""

reader.info.printInfo('.')