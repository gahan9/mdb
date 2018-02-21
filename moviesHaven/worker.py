import os
import tempfile
import re

from .models import Movie

SUPPORTED_EXTENSIONS = ['mp4', 'mkv', '3gp', 'avi', 'mov', 'vob', 'm3u8']


def name_fetcher(arg):
    return ' '.join(arg.split('_')[1].split('.')[:-1])


def filter_film(inputStr):
    import re
    # inputStr = name_fetcher(regexIn)
    regex = r"[s]\d+[e]\d+"
    regexOut = re.findall(regex, str(inputStr).lower())
    regSea = re.findall(r"[s]\d+", (str(regexOut).split(',')[0]).lower())
    regEpi = re.findall(r"[e]\d+", (str(regexOut).split(',')[0]).lower())
    tup = regSea, regEpi
    return tup


def content_fetcher(directory_path):
    data_set = []
    if os.path.exists(directory_path):
        for root, directory, files in os.walk(directory_path, topdown=True):
            for name in files:
                if name.split('.')[-1] in SUPPORTED_EXTENSIONS:
                    d = {"name": name, "path": root, "extension": name.split('.')[-1]}
                    data_set.append(d)
        return data_set
    else:
        return "Path Does not exist"


def data_assigner():
    contents = content_fetcher(directory_path=r"E:\dir")
    for video in contents:
        print(video)
        x = Movie.objects.filter()  # Keep movie as model arg
        return x

def getVideoDetails(filepath):
    tmpf = tempfile.NamedTemporaryFile()
    os.system("ffmpeg -i \"%s\" 2> %s" % (filepath, tmpf.name))
    lines = tmpf.readlines()
    tmpf.close()
    metadata = {}
    for l in lines:
        l = l.strip()
        if l.startswith('Duration'):
            metadata['duration'] = re.search('Duration: (.*?),', l).group(0).split(':',1)[1].strip(' ,')
            metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", l).group(0).split(':')[1].strip()
        if l.startswith('Stream #0:0'):
            metadata['video'] = {}
            metadata['video']['codec'], metadata['video']['profile'] = \
                [e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
            metadata['video']['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
            metadata['video']['bitrate'] = re.search('(\d+ kb/s)', l).group(1)
            metadata['video']['fps'] = re.search('(\d+ fps)', l).group(1)
        if l.startswith('Stream #0:1'):
            metadata['audio'] = {}
            metadata['audio']['codec'] = re.search('Audio: (.*?) ', l).group(1)
            metadata['audio']['frequency'] = re.search(', (.*? Hz),', l).group(1)
            metadata['audio']['bitrate'] = re.search(', (\d+ kb/s)', l).group(1)
    print(metadata)

# getVideoDetails(r"E:/dir/P27SXRNDxK_KLotZ-pronchic.mp4_a55d6.mp4")

if __name__ == "__main__":
    l = content_fetcher(directory_path=r"E:\dir")
    print(l)
