from imdbmovies import IMDB
imdb = IMDB()
res = imdb.get_by_name('House Of The Dragon', tv=True)
print(res)


import requests

img_data = requests.get(res["poster"]).content
with open('image_name.jpg', 'wb') as handler:
    handler.write(img_data)



from imdbmovies import IMDB
imdb = IMDB()
res = imdb.get_by_name('Dune', tv=False)
print(res)
