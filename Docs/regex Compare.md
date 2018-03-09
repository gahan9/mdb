PlanetVision
==========
> This document is to illustrate the power of capturing name of movie and tv episode from random unstructured files develop by Quixom Technology and other tools

What we provide
---------------------
We have developed a program which is able to detect number of valid file names and format(i.e. `mp4, m3u8`)
The success ratio of our program is top of the all considering all the various name we found

Comparison with XBMC Media Move 
--------------------------------------------
site url
: https://sourceforge.net/projects/xbmcmediamove/

- the biggest drawback of this package is that it is only designed to work on windows only hence it can not be deployed to existing data server
- even for power of capturing media it requires custom filter (regex) to be enter to being able to capture tv or movie name from unstructured files and we already have a much better filter (regex) running currently on server which is able to capture names of tv and movie files
- compare to this package we are able to handle many various cases of name 

Comparison with Emby
----------------------------
site url
: https://emby.media/

- Emby is a great package containing various feature like playing media, getting information etc.
- Emby is required to host it's own server to capture file and media
- compare to many of it's feature it's file name capturing capability is very low in exceptional cases.
- while our program able to capture information for about 22 content (including movie and tv) emby is able to capture only 2 contents from structure of 30 file cases

Comparison with FileBot
---------------------
site url
: https://www.filebot.net/

- compare to other tool Filebot do provide some of it's functionalities for command line argument
- it has only few regex to match the file name which won't give you better success ration for various other names
- the built in regex provided by filebot is just able to capture some common name only and hence compare to our program it's success ratio is not good enough

