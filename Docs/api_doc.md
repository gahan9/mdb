APIs
====
### DOMAIN: http://192.168.5.47:8000
----------
----------

Movie
--------
> **url**: *domain*/moviesHaven/api/movie/
> **method**: GET
> **params** (all optional)
> **no parameters** will list out all available movies
> **parameters**
>  :  **name** = the  # returns list of movies containing this string (Case insensitive)
>  : **name_starts_with** = A  # returns list of movies starts with this string (Case insensitive) 
> : **year** = 2018   # returns list of movies with release year
> : **genre** = animation  # returns list of movies containing this string as genre (Case insensitive) 
> : **latest** = 3  #  returns list of movies added/updated in last 3 days
> : **classics** = true  # returns result of movies since year Jan 1, 1900 to Jan 1, 1970
>  : **ordering** = name # available ordering name, release_date, vote_average, vote_count (name orders list of movies in ascending order whereas -name orders in descending order)
----------
### Sample URL
```
http://192.168.5.47:8000/moviesHaven/api/movie/?name\_starts\_with=i&name=r&year=1901&genre=drame&latest=1&ordering=name
```
Generate Stream
---------------------
> URL : 
> method : POST
> post-data format: json
> post-data
 ```
 {
	"id": 65,  # id of content
	"type": "movie",   # type of content movie or tv
	"stream_key": "eb17783d-bbbc-4499-ad74-eecd59c74baa"  # your streaming key
}
 ```
 Response
 ```
 {
    "stream_link": "http://192.168.5.47:8000/media/.cache/ab32c178-1af7-11e8-8ae2-e03f49b35bd1c"  # stream link of user
}
```
### Sample URL
```
http://192.168.5.47:8000/moviesHaven/api/generate_stream/```
