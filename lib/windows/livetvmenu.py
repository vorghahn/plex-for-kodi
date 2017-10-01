import xbmc
import xbmcgui
import kodigui
import windowutils
import m3u8reader
import smoothstreamstv
from lib import util
from lib.util import T
from lib import tvheadend
import home

from lib import player

import plexnet
from plexnet import plexapp

import subprocess
import sys

CHANNELDICT = {}

class settype():
    def __init__(self,settype):
        global PLAYLISTTYPE
        PLAYLISTTYPE = settype
        self.playlist = settype

class channel():
    def __init__(self, chnum=0, name='', url=''):
        self.ID = 0
        self.chnum = chnum
        self.name = name
        self.desc = ''
        self.url = url
        self.epgid = ''
        self.epgurl = ''
        self.logo = ''
        self.items = []

    def __getitem__(self):
        return self

class program():
    def __init__(self):
        self.eventID = 0
        self.episodeID = 0
        self.chname = ''
        self.chID = 0
        self.chnum = 0
        self.chIcon = ''
        self.start = 0
        self.stop = 0
        self.name = ''
        self.genre = ''
        self.nextEventID = 0
        self.description = ''
        self.language = 'en'
        self.runtime = 0

    def __getitem__(self):
        return self

class Channels(object):
    def __init__(self):
        self._ptype = ''
        self.ptype = PLAYLISTTYPE
        self.CHANNELS = {}
        self.CHANNEL_IDS = []
        self.CHANNELDICT = {}

    def update(self):
        global CHANNELDICT
        global CHANNELS
        global CHANNEL_IDS
        # CHANNELDICT = {}
        ptype = self.ptype
        util.ERROR("chan %s" % PLAYLISTTYPE)
        if ptype == 'm3u8':
            self.CHANNELDICT = m3u8reader.readfile()
        elif ptype == 'tvh':
            self.CHANNELDICT = tvheadend.gather('chan')
        elif ptype == 'sstv':
            self.CHANNELDICT = smoothstreamstv.gather('chan')
        else:
            util.ERROR('nil chan')
        self.CHANNELS = {}
        self.CHANNEL_IDS = []
        chan = []
        for i in self.CHANNELDICT:
            channel = self.CHANNELDICT[i]
            cnum = channel.chnum
            cname = channel.name
            clogo = channel.logo
            self.CHANNELS[i] = channel
            self.CHANNEL_IDS.append(cnum)
        # afile = open('c:/test/channellog.txt', 'w')
        # for i in CHANNELDICT:
        #     channel = CHANNELDICT[i]
        #     cnum = channel.chnum
        #     cname = channel.name
        #     clogo = channel.logo
        #     afile.write(str(cnum))
        #     afile.write(str(cname))
        #     afile.write(str(channel.url))
        #     afile.write(str(clogo))
        #     afile.write("\n")
        # afile.close()
        # CHANNEL_IDS = [i for i in range(1,len(CHANNELDICT)+1)]
        # CHANNEL_IDS.append('about')

    @property
    def ptype(self):
        return self._ptype

    @ptype.setter
    def ptype(self, ptype):
        self._ptype = PLAYLISTTYPE

    def __getitem__(self, key):
        return self.CHANNELS[key]

class Schedules(object):
    def __init__(self):
        self._ptype = ''
        self.ptype = PLAYLISTTYPE
        self.SCHEDULES = {}
        self.SCHEDULE_IDS = []
        self.SCHEDULEDICT = {}
    # util.ERROR("sched early %s" % PLAYLISTTYPE)
    def update(self):
        global SCHEDULES
        global SCHEDULE_IDS
        global SCHEDULEDICT
        SCHEDULEDICT = {}
        util.ERROR("sched %s" % PLAYLISTTYPE)
        ptype = self.ptype
        if ptype == 'm3u8':
            util.ERROR('m3u8sched')
            self.SCHEDULEDICT = m3u8reader.readfile()
        elif ptype == 'tvh':
            util.ERROR('tvhsched')
            self.SCHEDULEDICT = tvheadend.gather('epg')
        elif ptype == 'sstv':
            util.ERROR('sstvsched')
            self.SCHEDULEDICT = smoothstreamstv.gather('epg')
        else:
            util.ERROR('nil sched')
            self.SCHEDULES = {}
            self.SCHEDULE_IDS = []
        chan = []
        for i in self.SCHEDULEDICT:
            program = self.SCHEDULEDICT[i]
            # cnum = channel.chnum
            # cname = channel.name
            # clogo = channel.logo
            self.SCHEDULES[i] = program
            # SCHEDULE_IDS.append(cnum)
        # afile = open('c:/test/channellog.txt', 'w')
        # for i in CHANNELDICT:
        #     channel = CHANNELDICT[i]
        #     cnum = channel.chnum
        #     cname = channel.name
        #     clogo = channel.logo
        #     afile.write(str(cnum))
        #     afile.write(str(cname))
        #     afile.write(str(channel.url))
        #     afile.write(str(clogo))
        #     afile.write("\n")
        # afile.close()
        # CHANNEL_IDS = [i for i in range(1,len(CHANNELDICT)+1)]
        # CHANNEL_IDS.append('about')

    def __getitem__(self, key):
        return self.SCHEDULES[key][0]

class ChannelsWindow(kodigui.BaseWindow, windowutils.UtilMixin):
    xmlFile = 'script-plex-epg.xml'
    path = util.ADDON.getAddonInfo('path')
    theme = 'Main'
    res = '1080i'
    width = 1920
    height = 1080

    CHANNEL_LIST_ID = 60
    # SUB_CHANNELS_LIST_ID = 100
    TOP_GROUP_ID = 200
    SCHEDULE_LIST_ID = 100

    CLOSE_BUTTON_ID = 201
    PLAYER_STATUS_BUTTON_ID = 204

    def onFirstInit(self):
        # util.ERROR("win %s" % ptype)
        # global PLAYLISTTYPE
        # PLAYLISTTYPE = ptype
        self.channels = Channels()
        self.schedules = Schedules()
        self.channels.update()
        self.schedules.update()
        self.channelList = kodigui.ManagedControlList(self, self.CHANNEL_LIST_ID, 6)
        # self.subChannelsList = kodigui.ManagedControlList(self, self.SUB_CHANNELS_LIST_ID, 6)
        self.scheduleList = kodigui.ManagedControlList(self, self.SCHEDULE_LIST_ID, 6)
        self.setProperty('heading', T(32059, 'Channels'))
        self.showChannels()
        self.showSchedules()
        self.setFocusId(75)
        self.lastChannel = None
        self.checkChannel()



    # def onAction(self, action):
    #     try:
    #         self.checkChannel()
    #         controlID = self.getFocusId()
    #         # if action in (xbmcgui.ACTION_NAV_BACK, xbmcgui.ACTION_PREVIOUS_MENU):
    #         #     if self.getFocusId() == self.OPTIONS_LIST_ID:
    #         #         self.setFocusId(self.SUB_CHANNELS_LIST_ID)
    #         #         return
    #         #     # elif not xbmc.getCondVisibility('ControlGroup({0}).HasFocus(0)'.format(self.TOP_GROUP_ID)):
    #         #     #     self.setFocusId(self.TOP_GROUP_ID)
    #         #     #     return
    #         # elif action == xbmcgui.ACTION_MOVE_RIGHT and controlID == 150:
    #         #     self.editSetting(from_right=True)
    #     except:
    #         util.ERROR()
    #
    #     kodigui.BaseWindow.onAction(self, action)

    def onClick(self, controlID):
        if controlID == self.CHANNEL_LIST_ID:
            mli = self.channelList.getSelectedItem()
            setting = mli.dataSource
            chanNum = setting
            self.channelClicked(chanNum)
        elif controlID == self.SCHEDULE_LIST_ID:
            mli = self.scheduleList.getSelectedItem()
            setting = mli.dataSource
            chanNum = setting
            self.channelClicked(chanNum)
        # elif controlID == self.SUB_CHANNELS_LIST_ID:
        #     a = 1
        elif controlID == self.CLOSE_BUTTON_ID:
            self.doClose()
        elif controlID == self.PLAYER_STATUS_BUTTON_ID:
            a = 1

    def checkChannel(self):
        mli = self.channelList.getSelectedItem()
        if not mli:
            return

        if mli.dataSource == self.lastChannel:
            return

        self.lastChannel = mli.dataSource
        # self.showSubChannels(self.lastChannel)
        self.setProperty('section.about', self.lastChannel == 'about' and '1' or '')
        util.DEBUG_LOG('Vhannels: Changed channel ({0})'.format(self.lastChannel))

    def showChannels(self):
        items = []
        for i in self.channels.CHANNEL_IDS:
            try:
                label = self.channels.CHANNELS[i].name
                item = kodigui.ManagedListItem(label, data_source=i, iconImage=self.channels.CHANNELS[i].logo)
                items.append(item)
            except:
                util.ERROR('Null channel %s'.format(i))

        self.channelList.addItems(items)
        # self.subChannelsList.addItems(items)

    def showSchedules(self):
        if PLAYLISTTYPE == 'm3u8':
            return
        items = []
        # progs = smoothstreamstv.gather('epg')
        progs = self.schedules.SCHEDULEDICT
        import time
        # time.sleep(30)
        for j in self.channels.CHANNEL_IDS:
            try:
                chan = progs[int(j)][0]
                label = chan.name
                icon = chan.chIcon
                if progs[int(j)] == []:
                    item = kodigui.ManagedListItem("", data_source=j, iconImage=icon)
                else:
                    item = kodigui.ManagedListItem(label, data_source=j, iconImage=icon)

            except:
                item = kodigui.ManagedListItem("", data_source=j, iconImage="")
                util.ERROR('Null program on channel %s' % j)
            items.append(item)
        # for i in self.channels.CHANNEL_IDS:
        #     try:
        #         label = self.channels[i].items[0].chname
        #         item = kodigui.ManagedListItem(label, data_source=i, iconImage=self.channels[i].logo)
        #         items.append(item)
        #     except:
        #         util.ERROR('Null channel %s'.format(self.channels[i].name))
        self.scheduleList.addItems(items)


    def channelClicked(self, channelNumber):
        progs = self.schedules.SCHEDULEDICT

        #
        # if plexapp.INTERFACE.setPreference("live_tv_playlist", 'm3u8'):
        #     CHANNELDICT = m3u8reader.readfile()
        # elif plexapp.INTERFACE.setPreference("live_tv_playlist", 'tvh'):
        #     CHANNELDICT = tvheadend.gather()[0]
        channel = self.channels.CHANNELDICT[int(channelNumber)]
        url = util.addURLParams(channel.url, {
            'X-Plex-Platform': 'Chrome',
            'X-Plex-Client-Identifier': plexapp.INTERFACE.getGlobal('clientIdentifier')
        })
        li = xbmcgui.ListItem(channel.name, path=channel.url, thumbnailImage=channel.logo)
        try:
            chan = progs[int(channelNumber)][0]
            info = {'Title': chan.name,
                    'Genre': chan.genre,
                    'Plot':chan.description or chan.name
            }
            li.setInfo('video', info)
            player.PLAYER.play(url, li)
        except:
            player.PLAYER.play(url, li)



    # def channelClicked2(self, channelNum):
    #     url1 = "http://dap.smoothstreams.tv:9100/viewstvn/ch%sq1.stream/playlist.m3u8?wmsAuthSign=c2VydmVyX3RpbWU9OC8zMS8yMDE3IDU6NTk6MjEgQU0maGFzaF92YWx1ZT1zQnZCSS9FUU5LK3lCeS93bERZYjZBPT0mdmFsaWRtaW51dGVzPTI0MCZpZD12aWV3c3R2bi03MTM4==" % ('%02d' % int(channelNum))
    #     url = util.addURLParams(url1, {
    #         'X-Plex-Platform': 'Chrome',
    #         'X-Plex-Client-Identifier': plexapp.INTERFACE.getGlobal('clientIdentifier')
    #     })
    #     li = xbmcgui.ListItem("SSTV Test", path=url, thumbnailImage='script.plex/home/device/plex.png')
    #     player.PLAYER.play(url, li)


def openWindow():
    w = ChannelsWindow
    w.open()
    del w

def callM3u8():
    child = subprocess.Popen("python SmoothPlaylist.py", shell=True, stderr=subprocess.PIPE)
    while True:
        out = child.stderr.read(1)
        if out == '' and child.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()
