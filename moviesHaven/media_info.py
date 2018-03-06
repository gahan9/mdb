# coding=utf-8
import os
import sys
import re


class FetchMediaInfo(object):
    """
    Usage Example:
    action to be perform:
        ffprobe -v error -show_format -show_streams path/to/video.mp4

    """

    def __init__(self):
        self.platform = sys.platform
        self.base_command = "ffprobe -v error -show_format -show_streams "

    def get_all_info(self, media_path=None):
        """

        :param media_path:  media path
        :return:
        """
        media_info = {}
        # print("*"*25)
        # print(media_path)
        if not os.path.exists(media_path):
            print("MediaInfo: fetching unsuccessful\nreason: Media path not exist")
            return False

        if not self.platform == "win32":
            try:
                cmd = "{} '{}'".format(self.base_command, media_path)
                # print("cmd:-----------> {}".format(cmd))
                try:
                    try:
                        media_data = os.popen(cmd).read().encode('utf-8')
                    except Exception as e:
                        print("MediaInfo: unable to fetch media information \nreason: {}".format(e))
                        return False
                    # print(media_data)
                    media_info["frame_width"] = re.findall(r'width=(\d+)', media_data)[0]
                    media_info["frame_height"] = re.findall(r'height=(\d+)', media_data)[0]
                    media_info["runtime"] = re.findall(r'duration=(\d+)', media_data)[0]
                    media_info["video_codec"] = re.findall(r'codec_name=(\w+)', media_data)[0]
                    try:
                        media_info["audio_codec"] = re.findall(r'codec_name=(\w+)', media_data)[1]
                    except Exception as e:
                        print("MediaInfo: fetching audio_codec unsuccessful\nreason: {}".format(e))
                        # raise Exception(e)
                    try:
                        media_info["bit_rate"] = re.findall(r'bit_rate=(\w+)', media_data)[0]
                    except Exception as e:
                        print("MediaInfo: fetching bit_rate unsuccessful\nreason: {}".format(e))
                        # raise Exception(e)
                    return media_info
                except Exception as e:
                    print("MediaInfo: fetching unsuccessful\nreason: {}".format(e))
                    # raise Exception(e)
                    return False
            except Exception as e:
                print("MediaInfo: cmd fetching unsuccessful\nreason: {}".format(e))
                # raise Exception(e)
                return False
