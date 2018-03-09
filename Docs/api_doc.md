APIs
====
### DOMAIN: http://192.168.5.47:8000
----------
**movie**				: http://54.36.48.153:8000/api/movie/
**tv**						: http://54.36.48.153:8000/api/tv/
**season**				: http://54.36.48.153:8000/api/season/
**episode**           	: http://54.36.48.153:8000/api/episode/
**person**            	: http://54.36.48.153:8000/api/person/
**genre_movie**	: http://54.36.48.153:8000/api/genre_movie/
**person_movie**	: http://54.36.48.153:8000/api/person_movie/
**genre_tv**			: http://54.36.48.153:8000/api/genre_tv/
 
----------

Movie
=====
/api/movie/
--------------
> **url**: *domain*/moviesHaven/api/movie/
> **method**: GET
> **params** (all optional)
> **no parameters** will list out all available movies
> **parameters**
>  :  **name** = the  # returns list of movies containing this string (Case insensitive)
>  : **name_starts_with** = A  # returns list of movies starts with this string (Case insensitive) 
>   if **name_starts_with** = 0 # will return list of all movies starts with number *[0-9]*
> : **year** = 2018   # returns list of movies with release year
> : **genre** = animation  # returns list of movies containing this string as genre (Case insensitive) 
> : **latest** = 3  #  returns list of movies added/updated in last 3 days
> : **classics** = true  # returns result of movies since year Jan 1, 1900 to Jan 1, 1970
>  : **ordering** = name # available ordering *name, release_date, vote_average, vote_count* (name orders list of movies in ascending order whereas *-name* orders in descending order)
>  : **person_name**=Dwayne%20Johnson  # get list of movies by this cast/actor
>  : **exclude**=true  # remove movies with genre animation and documentrie
----------
### Sample URL
```
http://192.168.5.47:8000/moviesHaven/api/movie/?name\_starts\_with=i&name=r&year=1901&genre=drame&latest=1&ordering=name
```
Movie By Genre
--------------------
/api/genre_movie/
--------------
***Step 1***
: URL: *domain*/moviesHaven/api/genre_movie/
 Response Type: json
 Response:  list of genres
 
### Sample URL
```
http://192.168.5.47:8000/moviesHaven/api/genre_movie/
```
select genre_name

 -------------
 **Step 2**
 : **url**: *domain*/moviesHaven/api/movie/
  **params**: genre= genre_name  # genre_name from step 1


Person
======
api/person
-------------
> URL : *domain*/moviesHaven/api/person
> method : GET
> post-data format: json
> post-data
> **params**:
> **type**: movie/tv
> **name_starts_with** : a   # returns list of actors of given type starts with

### Sample URL
```
http://192.168.5.47:8000/moviesHaven/api/person/?name_starts_with=d&type=movie
```
Now hi below url with selecting name from response of above api as below:
```
http://192.168.5.47:8000/moviesHaven/api/movie/?person_name=Dwayne%20Johnson
```

Generate Stream
=============
/api/generate_stream
--------------------------
> URL : *domain*/moviesHaven/api/generate_stream
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
```http://192.168.5.47:8000/moviesHaven/api/generate_stream/```

