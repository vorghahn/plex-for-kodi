import livetvmenu
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
#         self.items = []

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def readfile():

    afile = open("c:\kiwitv2.m3u", 'r')
    afile.readline()
    cdict = {}
    for channelNum in range(1,151):
        channel = livetvmenu.channel()

        #example m3u8 line
        #Line 1 #EXTINF:-1 tvg-id="tv.9" tvg-logo="http://www.freeviewnz.tv/nonumbracoimages/ChannelsOpg/TVNZ11280x1280.png",TVNZ 1
        #Line 2 https://tvnzioslive04-i.akamaihd.net/hls/live/267188/1924997895001/channel1/master.m3u8|X-Forwarded-For=219.88.222.91

        # #EXTINF:-1 tvg-id="133" tvg-logo="https:https://guide.smoothstreams.tv/assets/images/channels/110.png" tvg-name="BT Sport 3 HD" tvg-num="110",BT Sport 3 HD
        # pipe://#PATH# 110
        header = afile.readline()
        if header:
            channel.url=afile.readline().strip()
            header = header.strip("\n")
            header = header.split(",")
            metadata = header[0]
            channel.name=header[1]
            metadata = metadata.split(" ")
            for item in metadata:
                if item == "#EXTINF:-1":
                    pass
                elif "tvg-id" in item:
                    channel.ID=find_between(item,'"','"')
                elif "tvg-logo" in item:
                    channel.logo=item[10:-1]
                elif "tvg-name" in item:
                    channel.name=item[10:-1]
                elif "tvh-chnum" in item:
                    channel.chnum=int(item[11:-1])
                elif "epg-id" in item:
                    channel.epgid=item[8:-1]
                elif "url-epg" in item:
                    channel.epgurl=item[9:-1]
            if channel.chnum == 0:
                channel.chnum = channelNum
            cdict[channel.chnum] = channel

    return cdict
