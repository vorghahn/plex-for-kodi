import livetvmenu
import urllib2
import json
import urllib
from lib import util
import plexnet
from plexnet import plexapp
from getpass import getpass
from json import loads, dumps
from os import path
from urllib2 import urlopen
from xml.sax.saxutils import escape
import os.path
from os.path import expanduser
import time
import json
import argparse
import re
#
# class channel1():
#     def __init__(self, chnum=0, name='', url=''):
#         self.ID = 0
#         self.chnum = chnum
#         self.name = name
#         self.desc = ''
#         self.url = url
#         self.epgid = ''
#         self.epgurl = ''
#         self.logo = ''
#
# class program():
#     def __init__(self):
#         self.eventID = 0
#         self.episodeID = 0
#         self.chname = ''
#         self.chID = 0
#         self.chnum = 0
#         self.chIcon = ''
#         self.start = 0
#         self.stop = 0
#         self.name = ''
#         self.genre = ''
#         self.nextEventID = 0
#         self.description = ''
#         self.language = 'en'
#         self.runtime = 0

def gather(request):

    global config

    # try:
    #     with open('c:\sstv-config.json') as jsonConfig:
    #         config = json.load(jsonConfig)
    # except:
    # util.ERROR("Invalid config file. Using defaults.")
    config = {
        "quality": 1,
        "checkChannel": True,
        "includeBadChannels": False,
        "httpTimeoutChannel": 1,
        "username": "",
        "password": "",
        "server": "",
        "rtmp": False,
        "service": "",
        "minQuality": 0,
        "guideLookAheadMinutes": 5,
        "guideMaxFutureMinutes": 240,
        "tvheadend": False,
        "debug": False
        }
    if not "quality" in config or not isinstance(config["quality"], int):
        config["quality"] = 1
    if not "checkChannel" in config:
        config["checkChannel"] = True
    if not "includeBadChannels" in config:
        config["includeBadChannels"] = True
    if not "httpTimeoutChannel" in config or not (
        isinstance(config["httpTimeoutChannel"], int) or isinstance(config["httpTimeoutChannel"], float)) or config[
        "httpTimeoutChannel"] < 0 or config["httpTimeoutChannel"] > 15:
        config["httpTimeoutChannel"] = 1
    if not "username" in config:
        config["username"] = ""
    if not "password" in config:
        config["password"] = ""
    if not "server" in config:
        config["server"] = ""
    if not "rtmp" in config:
        config["rtmp"] = False
    if not "service" in config:
        config["service"] = ""
    if not "minQuality" in config or not isinstance(config["minQuality"], int) or config["minQuality"] < 0 or config[
        "minQuality"] > 1080:
        config["minQuality"] = 0
    if not "guideLookAheadMinutes" in config or not isinstance(config["guideLookAheadMinutes"], int) or config[
        "guideLookAheadMinutes"] < 0 or config["guideLookAheadMinutes"] > 1440:
        config["guideLookAheadMinutes"] = 5
    if not "debug" in config or not isinstance(config["debug"], bool):
        config["debug"] = False
    if not "guideMaxFutureMinutes" in config or not isinstance(config["guideMaxFutureMinutes"], int) or config[
        "guideMaxFutureMinutes"] < 0 or config["guideMaxFutureMinutes"] > 1680:
        config["guideMaxFutureMinutes"] = 240
    if not "tvheadend" in config:
        config["tvheadend"] = False
    if not "outputDirectory" in config:
        config["outputDirectory"] = os.getcwd()
    if not "alturl" in config:
        config["alturl"] = False

    config["quality"] = plexapp.INTERFACE.getPreference("sstv_quality")
    config["service"] = plexapp.INTERFACE.getPreference("service_sstv")
    config["username"] = plexapp.INTERFACE.getPreference("uname_sstv")
    config["password"] = plexapp.INTERFACE.getPreference("pword_sstv")
    config["server"] = plexapp.INTERFACE.getPreference("server_sstv")

    if (config["guideLookAheadMinutes"] > 29):
        config["checkChannel"] = False



    # print(config)
    # print('Generating playlist')
    cachedir = expanduser("~")
    cachefile = os.path.join(cachedir, "sstv.json")
    jsonGuide1 = getJSON(cachefile,"http://sstv.fog.pt/feedall1.json","https://guide.smoothstreams.tv/feed.json", "https://iptvguide.netlify.com/iptv.json")
    authSign = getAuthSign(config["username"], config["password"])
    util.ERROR('hash follows')
    util.ERROR(authSign)
    cdict = getChannels(config["server"],config["rtmp"], config["service"], config["quality"], authSign, jsonGuide1, config["alturl"])

    address = 'http://sstv.fog.pt/feedall1.json'
    response = urllib2.urlopen(address)

    # {"1":
    # {"channel_id": "1",
    # "img": "https://guide.smoothstreams.tv/assets/images/channels/1.png",
    # "items": [
    #     {"category": "Baseball", "channel": "1", "description": "MLB: Washington Nationals at Miami Marlins",
    #      "end_time": "2017-09-05 22:00:00", "id": "208511", "language": "us",
    #      "name": "MLB: Washington Nationals at Miami Marlins", "quality": "720p", "runtime": "180", "source": "ss",
    #      "time": "2017-09-05 19:00:00", "version": "None"},

    #     {"category": "Baseball", "channel": "1", "description": "MLB: Philadelphia Phillies at New York Mets",
    #      "end_time": "2017-09-04 16:00:00", "id": "208490", "language": "us",
    #      "name": "MLB: Philadelphia Phillies at New York Mets", "quality": "720p", "runtime": "180", "source": "ss",
    #      "time": "2017-09-04 13:00:00", "version": "None"}],
    #        "name": "01 - ESPNNews"},

    data = json.load(response)
    epgdict = {}
    for chan in jsonGuide1:
        counter = 0
        epgdict[int(chan)] = []
        for item in data[chan]['items']:
            prog = livetvmenu.program()
            prog.eventID = item.get('id')
            # prog.episodeID = item.get('episodeId')
            prog.chname = item.get('name')
            # prog.chID = item.get('channelUuid')
            prog.chnum = int(item.get('channel'))
            prog.chIcon = data[chan].get('img')
            prog.start = item.get('time')
            prog.stop = item.get('end_time')
            prog.name = item.get('name')
            prog.genre = item.get('category')
            prog.nextEventID = item.get('nextEventId')
            prog.description = item.get('nextEventId')
            prog.language = item.get('language')
            prog.runtime = item.get('runtime')
            # epgdict[int(chan)].append(prog)
            # cdict[int(chan)]['items'].append(prog)
            epgdict[int(chan)].append(prog)
            counter += 1

    if request == 'chan':
        return cdict
    else:
        return epgdict

# print gather('chan')


def getJSON(sFile, sURL, sURL2, sURL3):

    try:
        if os.path.isfile(sFile) and time.time() - os.stat(sFile).st_mtime < 7200:
            retVal = json.loads(open(sFile, 'r').read())
            return retVal
    except:
        pass

    try:
        util.ERROR(sURL)
        sJSON = urllib2.urlopen(sURL).read().decode("utf-8")
        retVal = json.loads(sJSON)
        print sURL
    except:
        try:
            util.ERROR(sURL2)
            sJSON = urllib2.urlopen(sURL2).read().decode("utf-8")
            retVal = json.loads(sJSON)
            print sURL2
        except:
            try:
                util.ERROR(sURL3)
                sJSON = urllib2.urlopen(sURL3).read().decode("utf-8")
                retVal = json.loads(sJSON)
                print sURL3
            except:
                print "fail"
                return json.loads("{}")

    # sJSON['hash'] = str(getAuthSign(config["username"], config["password"]))
    file = open(sFile, "w+")
    file.write(sJSON)

    file.close()
    return retVal

def getAuthSign(un, pw):
    '''request JSON from server and return hash'''
    try:
        sFile = os.path.join(expanduser("~"), 'sstvhash')
        if os.path.isfile(sFile) and time.time() - os.stat(sFile).st_mtime < 7200:
            f = open(sFile, 'r')
            util.ERROR('using existing hash')
            return f.readline()
    except:
        pass

    # url = 'http://auth.smoothstreams.tv/hash_api.php?username=' + urllib.quote_plus(un)+ '&password=' +urllib.quote_plus(pw)+ "&site=" + urllib.quote_plus(config["service"])
    post_data = {"username": un, "password": pw, "site": config["service"]}
    url = 'http://auth.smoothstreams.tv/hash_api.php?'
    values = urllib.urlencode(post_data)
    try:
        util.ERROR(url)
        util.ERROR(values)
        # response = urllib2.Request(url, values)
        url = (url + values).replace("+","")
        util.ERROR(url)
        response = urlopen(url).read().decode('utf-8')
        # util.ERROR(response)
        data = loads(response)
        if data['hash']:
            util.ERROR(data['hash'])
            file = open(os.path.join(expanduser("~"),'sstvhash'), "w+")
            file.write(data['hash'])
            file.close()
            return data['hash']

    except ValueError:
        util.ERROR('Unable to retrieve data from the server.\nPlease check your internet connection and try again.')
        exit(1)
    except KeyError:
        util.ERROR('There was an error with your credentials.\nPlease double-check your username and password and try again.')
        exit(1)


def getChannels(server, rtmp, service, streamQuality, authSign, jsonGuide1, alturl):
    if alturl:
        urlTemplate = alturl + ' {2}'
    elif rtmp:
        urlTemplate = 'rtmp://{0}.smoothstreams.tv:3625/{1}?wmsAuthSign={4}/ch{2}q{3}.stream'
    else:
        urlTemplate = 'http://{0}.smoothstreams.tv:9100/{1}/ch{2}q{3}.stream/playlist.m3u8?wmsAuthSign={4}=='
    iconTemplate = "http://guide.smoothstreams.tv/assets/images/channels/{0}.png"
    maxChannel = 0
    for item, x in iter(jsonGuide1.items()):
        if int(item) > maxChannel:
            maxChannel = int(item)

    cdict = {}
    # print jsonGuide1

    for i in range(1, maxChannel):
        chan = livetvmenu.channel()
        try:
            chan.name = jsonGuide1[str(i)]["name"]
            chan.name = chan.name.split('- ', 1)[-1].replace(" ", "").replace("720p", "")
        except:
            chan.name = str(i)
        if chan.name == "":
            chan.name = str(i)
        chan.ID = int(i)
        chan.logo = iconTemplate.format(i)
        chan.chnum = int(i)
        if i > 60:
            streamQuality = 1

        chan.url = urlTemplate.format(server, service, format(i, "02"), str(streamQuality), authSign).replace(" ","")
        # print chan, channel.name, channel.logo, channel.url
        cdict[chan.chnum] = chan
    return cdict

# print gather('chan')
