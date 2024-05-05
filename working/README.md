### See also VideoInfo Plugin

* https://github.com/C5H12O5/syno-videoinfo-plugin

### GitHub

* https://github.com/oPromessa/vsMetaFileEncoder
* https://gist.github.com/soywiz/2c10feb1231e70aca19a58aca9d6c16a


### Setup Environment

```sh
python3.11 -m venv venv
source venv/bin/activate
python3.11 -m pip install -e .
pip install imdbmovies
pip install requests
```

### Build up List of Movies


```sh
$ find  /Volumes/video/Movies/ \( -name Dune\* -o -name Voyagers\* -o -name Titanic\* \) ! -type d ! -name \*srt ! -name \*idx ! -name \*sub ! -name .DS_Store ! -name \*txt ! -name \*.vsmeta  | sed 's/\/Volumes\/video\/Movies\/\///'  | sort | python ../build_csv.py  > movie_titles.csv 
```

### Search and then copy back
```sh
$ python ../imdb2vsmeta.py
```

### Loading .vsmeta does not loadup DSVideo

* Trying Settings -> Library -> Movies -> Reindexing

