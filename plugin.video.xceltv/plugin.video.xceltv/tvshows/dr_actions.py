'''
Created on Feb 1, 2015

@author: jchirag

This file is part of XOZE. 

XOZE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

XOZE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with XOZE.  If not, see <http://www.gnu.org/licenses/>.
'''

from xoze.context import AddonContext, SnapVideo
from xoze.snapvideo import Dailymotion, Playwire, YouTube, Tune_pk, VideoWeed, \
    Nowvideo, Novamov, CloudEC, VideoHut, VideoTanker
from xoze.utils import file, http, jsonfile
from xoze.utils.cache import CacheManager
from xoze.utils.http import HttpClient
import BeautifulSoup
import base64
import logging
import pickle
import re
import time
import urllib
import urllib2
import json
import xbmc  # @UnresolvedImport
import xbmcgui  # @UnresolvedImport
import binascii, os

DIRECT_CHANNELS = {}
				 
live_channel_json_url = "https://raw.githubusercontent.com/sunnythakkar/xceltv/master/plugin.video.xceltv/4_channels.json"
response = urllib.urlopen(live_channel_json_url);
LIVE_CHANNELS = json.loads(response.read())

class NoRedirectionSpecial(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response

def get_softmag_key():
    iI111iI = urllib2.Request(base64.b64decode('aHR0cDovL3NvZnRtYWduYXRlLmNvbS9nZXRDaEtleTIucGhw'))
    IiII = urllib2 . urlopen ( iI111iI )
    iI1Ii11111iIi = IiII . read ( )
    return iI1Ii11111iIi

def check_cache(req_attrib, modelMap):
    logging.getLogger().debug('Check cache ***********************')
    logging.getLogger().debug(req_attrib)
    refresh_cache = True
    context = AddonContext()
    filepath = file.resolve_file_path(context.get_addon_data_path(), extraDirPath='data', filename='DR_Channels.json', makeDirs=True)
    refresh = context.get_addon().getSetting('drForceRefresh')
    if refresh == None or refresh != 'true':
        modified_time = file.get_last_modified_time(filepath)
        if modified_time is not None:
            diff = long((time.time() - modified_time) / 3600)
            if diff < 720:
                refresh_cache = False
            else:
                logging.getLogger().debug('DR_Channels.json was last created 30 days ago, refreshing data.')
    else:
        logging.getLogger().debug('Request to force refresh.')
    modelMap['refresh_cache'] = refresh_cache
    modelMap['cache_filepath'] = filepath


def refresh_cache(req_attrib, modelMap):
    if not modelMap['refresh_cache']:
        return
    logging.getLogger().debug('Reloading cache...')
    
    tv_data = {"channels": {}}
    current_index = 0
    tv_channels = tv_data['channels']
    total_iteration = len(tv_channels)
    progress_bar = modelMap['progress_control']
    channel_image = modelMap['channel_image_control']
    for tv_channel_name, tv_channel in tv_channels.iteritems():
        logging.getLogger().debug('About to retrieve tv shows for channel %s' % tv_channel_name)
        channel_image.setImage(tv_channel['iconimage'])
        channel_image.setVisible(True)
        __retrieve_channel_tv_shows__(tv_channel_name, tv_channel)
        channel_image.setVisible(False)
        current_index = current_index + 1
        percent = (current_index * 100) / total_iteration
        progress_bar.setPercent(percent)
        
    status = jsonfile.write_file(modelMap['cache_filepath'], tv_data)
    if status is not None:
        logging.getLogger().debug('Saved status = ' + str(status))
    CacheManager().put('tv_data', tv_data)
    AddonContext().get_addon().setSetting('drForceRefresh', 'false')
    
CHANNEL_TYPE_IND = 'IND'
CHANNEL_TYPE_TEL = 'TEL'
CHANNEL_TYPE_TAM = 'TAM'
CHANNEL_TYPE_KAN = 'KAN'
CHANNEL_TYPE_MAL = 'MAL'
CHANNEL_TYPE_MAR = 'MAR'
CHANNEL_TYPE_BEN = 'BEN'
CHANNEL_TYPE_PUN = 'PUN'
CHANNEL_TYPE_ORI = 'ORI'
CHANNEL_TYPE_GUJ = 'GUJ'
CHANNEL_TYPE_PAK = 'PAK'
CHANNEL_TYPE_BAN = 'BAN'
CHANNEL_TYPE_BHO = 'BHO'
CHANNEL_TYPE_SPO = 'SPO'
CHANNEL_TYPE_ENG = 'ENG'
CHANNEL_TYPE_KID = 'KID'
CHANNEL_TYPE_NEP = 'NEP'
CHANNEL_TYPE_AFG = 'AFG'

def load_channels(req_attrib, modelMap):
    logging.getLogger().debug('load channels...')
    tv_channels = _read_tv_channels_cache_(modelMap['cache_filepath'])['channels']
    
    tv_channel_items = []
    
    live_channels_all = {}
    live_channels_all.update(LIVE_CHANNELS)

    channel_names = live_channels_all.keys()
    channel_names.sort()
        
    showHindiChannels = AddonContext().get_addon().getSetting('drShowHindiChannels')
    showTeluguChannels = AddonContext().get_addon().getSetting('drShowTeluguChannels')
    showTamilChannels = AddonContext().get_addon().getSetting('drShowTamilChannels')
    showKannadaChannels = AddonContext().get_addon().getSetting('drShowKannadaChannels')
    showMalayalamChannels = AddonContext().get_addon().getSetting('drShowMalayalamChannels')
    showMarathiChannels = AddonContext().get_addon().getSetting('drShowMarathiChannels')
    showBengaliChannels = AddonContext().get_addon().getSetting('drShowBengaliChannels')
    showPunjabiChannels = AddonContext().get_addon().getSetting('drShowPunjabiChannels')
    showOriyaChannels = AddonContext().get_addon().getSetting('drShowOriyaChannels')
    showGujaratiChannels = AddonContext().get_addon().getSetting('drShowGujaratiChannels')
    showUrduChannels = AddonContext().get_addon().getSetting('drShowUrduChannels')
    showBanglaChannels = AddonContext().get_addon().getSetting('drShowBanglaChannels')
    showBhojpuriChannels = AddonContext().get_addon().getSetting('drShowBhojpuriChannels')
    showSportsChannels = AddonContext().get_addon().getSetting('drShowSportsChannels')
    showEnglishChannels = AddonContext().get_addon().getSetting('drShowEnglishChannels')
    showKidsChannels = AddonContext().get_addon().getSetting('drShowKidsChannels')
    showNepaleseChannels = AddonContext().get_addon().getSetting('drShowNepaleseChannels')
    showAfghanChannels = AddonContext().get_addon().getSetting('drShowAfghanChannels')
    
    for channel_name in channel_names:
        channel_obj = live_channels_all[channel_name]
        if(  (channel_obj['channelType'] == CHANNEL_TYPE_IND and showHindiChannels is not None and showHindiChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_TEL and showTeluguChannels is not None and showTeluguChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_TAM and showTamilChannels is not None and showTamilChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_KAN and showKannadaChannels is not None and showKannadaChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_MAL and showMalayalamChannels is not None and showMalayalamChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_MAR and showMarathiChannels is not None and showMarathiChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_BEN and  showBengaliChannels is not None and showBengaliChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_PUN and showPunjabiChannels is not None and showPunjabiChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_ORI and showOriyaChannels is not None and showOriyaChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_GUJ and showGujaratiChannels is not None and showGujaratiChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_PAK and showUrduChannels is not None and showUrduChannels == 'true') 
          or (channel_obj['channelType'] == CHANNEL_TYPE_BAN and showBanglaChannels is not None and showBanglaChannels == 'true')
          or (channel_obj['channelType'] == CHANNEL_TYPE_BHO and showBhojpuriChannels is not None and showBhojpuriChannels == 'true')
          or (channel_obj['channelType'] == CHANNEL_TYPE_SPO and showSportsChannels is not None and showSportsChannels == 'true')
          or (channel_obj['channelType'] == CHANNEL_TYPE_ENG and showEnglishChannels is not None and showEnglishChannels == 'true')
          or (channel_obj['channelType'] == CHANNEL_TYPE_KID and showKidsChannels is not None and showKidsChannels == 'true')
          or (channel_obj['channelType'] == CHANNEL_TYPE_NEP and showNepaleseChannels is not None and showNepaleseChannels == 'true')
          or (channel_obj['channelType'] == CHANNEL_TYPE_AFG and showAfghanChannels is not None and showAfghanChannels == 'true')
          ):            
            item = xbmcgui.ListItem(label=channel_name, iconImage=channel_obj['iconimage'], thumbnailImage=channel_obj['iconimage'])
            item.setProperty('channel-name', channel_name)
            item.setProperty('live-link', 'true')
            item.setProperty('direct-link', 'false')
            tv_channel_items.append(item)    
     
    modelMap['tv_channel_items'] = tv_channel_items
    

def load_favorite_tv_shows(req_attrib, modelMap):
    context = AddonContext()
    filepath = file.resolve_file_path(context.get_addon_data_path(), extraDirPath='data', filename='DR_Favorites.json', makeDirs=False)
    logging.getLogger().debug('loading favorite tv shows from file : %s' % filepath)
    favorite_tv_shows = _read_favorite_tv_shows_cache_(filepath)
    if favorite_tv_shows is None:
        return
    favorite_tv_shows_items = []
    for tv_show_name in favorite_tv_shows:
        favorite_tv_show = favorite_tv_shows[tv_show_name]
        item = xbmcgui.ListItem(label=tv_show_name, iconImage=favorite_tv_show['tv-show-thumb'], thumbnailImage=favorite_tv_show['tv-show-thumb'])
        item.setProperty('channel-type', favorite_tv_show['channel-type'])
        item.setProperty('channel-name', favorite_tv_show['channel-name'])
        item.setProperty('tv-show-name', tv_show_name)
        item.setProperty('tv-show-url', favorite_tv_show['tv-show-url'])
        item.setProperty('tv-show-thumb', favorite_tv_show['tv-show-thumb'])
        favorite_tv_shows_items.append(item)
        
    modelMap['favorite_tv_shows_items'] = favorite_tv_shows_items
    
def determine_direct_tv_channel(req_attrib, modelMap):
    if(req_attrib['direct-link'] == 'true'):
        logging.getLogger().debug('found direct channel redirect...')
        return 'redirect:dr-displayDirectChannelEpisodesList'
    
def determine_live_tv_channel(req_attrib, modelMap):
    if(req_attrib['live-link'] == 'true'):
        logging.getLogger().debug('found live channel redirect...')
        return 'redirect:dr-watchLiveChannel'
    

def load_tv_shows(req_attrib, modelMap):
    logging.getLogger().debug('load tv shows...')
    
    tv_channels = CacheManager().get('tv_data')['channels']
    channel_name = req_attrib['channel-name']
    tv_channel = tv_channels[channel_name]
    channel_type = tv_channel['channelType']
    modelMap['channel_image'] = tv_channel['iconimage']
    modelMap['channel_name'] = channel_name
    selected_tv_show_name = ''
    if req_attrib.has_key('tv-show-name'):
        selected_tv_show_name = req_attrib['tv-show-name']
    tv_show_items = []
    index = 0
    if tv_channel.has_key('running_tvshows'):
        tv_shows = tv_channel['running_tvshows']
        logging.getLogger().debug('total tv shows to be displayed: %s' % str(len(tv_shows)))
        index = _prepare_tv_show_items_(tv_shows, channel_type, channel_name, selected_tv_show_name, tv_show_items, False, modelMap, index)
    
    hideFinishedShow = AddonContext().get_addon().getSetting('drHideFinished')
    
    if tv_channel.has_key('finished_tvshows') and hideFinishedShow is not None and hideFinishedShow == 'false':
        tv_shows = tv_channel["finished_tvshows"]
        logging.getLogger().debug('total finsihed tv shows to be displayed: %s' % str(len(tv_shows)))
        index = _prepare_tv_show_items_(tv_shows, channel_type, channel_name, selected_tv_show_name, tv_show_items, True, modelMap, index)
        
    modelMap['tv_show_items'] = tv_show_items
    
def load_direct_link_channel(req_attrib, modelMap):
    channel_name = req_attrib['channel-name']
    tv_channel = DIRECT_CHANNELS[channel_name]
    
    modelMap['channel_image'] = tv_channel['iconimage']
    modelMap['channel_name'] = channel_name
    
    req_attrib['tv-show-url'] = BASE_WSITE_URL + tv_channel['tvshow_episodes_url']
    req_attrib['tv-show-name'] = ''
    req_attrib['channel-type'] = tv_channel['channelType']
    
def re_me(data, re_patten):
    match = ''
    m = re.search(re_patten, data)
    if m != None:
        match = m.group(1)
    else:
        match = ''
    return match        

def watch_live(req_attrib, modelMap):
    channel_name = req_attrib['channel-name']
    tv_channel = LIVE_CHANNELS[channel_name]
    item = xbmcgui.ListItem(label=channel_name, iconImage=tv_channel['iconimage'], thumbnailImage=tv_channel['iconimage'])

    final_url = tv_channel['channelUrl']

    #START SOFTMAG 
    if tv_channel['channelSource'] == 'SOFTMAG':
        key = get_softmag_key()
        final_url = final_url + key
    #END SOFTMAG

    # START EBOUND Links
    if tv_channel['channelSource'] == 'EBOUND':
        cName=final_url
        import math, random, time
        rv=str(int(5000+ math.floor(random.random()*10000)))
        currentTime=str(int(time.time()*1000))
        newURL=base64.b64decode('aHR0cDovL3d3dy5lYm91bmRzZXJ2aWNlcy5jb20vaWZyYW1lL25ldy9tYWluUGFnZS5waHA/c3RyZWFtPQ==')+cName+  '&width=undefined&height=undefined&clip=' + cName+'&rv='+rv+'&_='+currentTime
        req = urllib2.Request(newURL)
        req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        defaultStreamType=0 #0 RTMP
        post = {'username':'hash'}
        post = urllib.urlencode(post)
        req = urllib2.Request(base64.b64decode('aHR0cDovL2Vib3VuZHNlcnZpY2VzLmNvbS9mbGFzaHBsYXllcmhhc2gvaW5kZXgucGhw'))
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36')
        response = urllib2.urlopen(req,post)
        link=response.read()
        response.close()
        strval =link;# match[0]
        playfile=base64.b64decode('cnRtcDovL2Nkbi5lYm91bmQudHYvdHY/d21zQXV0aFNpZ249LyVzIGFwcD10dj93bXNBdXRoU2lnbj0lcyBzd2Z1cmw9aHR0cDovL3d3dy5lYm91bmRzZXJ2aWNlcy5jb20vbGl2ZS92Ni9qd3BsYXllci5mbGFzaC5zd2Y/ZG9tYWluPXd3dy5lYm91bmRzZXJ2aWNlcy5jb20mY2hhbm5lbD0lcyZjb3VudHJ5PUVVIHBhZ2VVcmw9aHR0cDovL3d3dy5lYm91bmRzZXJ2aWNlcy5jb20vY2hhbm5lbC5waHA/YXBwPXR2JnN0cmVhbT0lcyB0Y1VybD1ydG1wOi8vY2RuLmVib3VuZC50di90dj93bXNBdXRoU2lnbj0lcyBsaXZlPXRydWUgdGltZW91dD0xNQ==')%(cName,strval,cName,cName,strval)
        final_url = playfile
    # END EBOUND Links
    
     #EBOUNDNEW
    
    if tv_channel['channelSource'] == 'EBOUNDNEW':
    	
    	req = urllib2.Request('http://softmagnate.com/getChKey2.php')
    	response = urllib2.urlopen(req)
    	link = response.read()
    	response.close()
    	stream = final_url + '?wmsAuthSign=' + link
    	final_url = stream
    
    
    
    # START Jadoo Links 
    if tv_channel['channelSource'] == 'JADOO':
        if '?securitytype=2' in final_url:
            opener = urllib2.build_opener(NoRedirectionSpecial)
            response = opener.open(final_url)
            dag_url = response.info().getheader('Location')
        else:
            if '/play/' in final_url:
                code=base64.b64decode('MDAwNkRDODUz')+binascii.b2a_hex(os.urandom(2))[:3]
                final_url+=base64.b64decode('L1VTLzEv')+code
                getUrl(base64.b64decode('aHR0cDovL2ZlcnJhcmlsYi5qZW10di5jb20vaW5kZXgucGhwL3htbC9pbml0aWFsaXplLzA1LTAyLTEzMDEwNy0yNC1QT1AtNjE4LTAwMC8yLjIuMS40Lw==')+code)
            req = urllib2.Request(final_url)
            req.add_header('User-Agent', base64.b64decode('VmVyaXNtby1CbGFja1VJXygyLjQuNy41LjguMC4zNCk='))
            response = urllib2.urlopen(req)        
            link=response.read()

            if '[CDATA' in link:
                link=link.split('CDATA[')[1].split(']')[0]#
                dag_url = link
            else:
                curlpatth='\<ENTRY\>\<REF HREF="(.*?)"'
                dag_url =re.findall(curlpatth,link)[0]
            
            if 'dag1.asx' in dag_url:
                req = urllib2.Request(dag_url)
                req.add_header('User-Agent', 'Verismo-BlackUI_(2.4.7.5.8.0.34)')   
                response = urllib2.urlopen(req)
                link=response.read()
                dat_pattern='href="([^"]+)"[^"]+$'
                dag_url =re.findall(dat_pattern,link)[0]
                
            if '127.0.0.1' in dag_url:
                final_url = re_me(dag_url, '&ver_t=([^&]+)&') + ' live=true timeout=15 playpath=' + re_me(dag_url, '\\?y=([a-zA-Z0-9-_\\.@]+)')
                if 'devinlivefs.fplive.net' not in final_url:
                    final_url = final_url.replace('devinlive', 'flive')
                if 'permlivefs.fplive.net' not in final_url:
                    final_url = final_url.replace('permlive', 'flive')         
            elif re_me(dag_url, 'wmsAuthSign%3D([^%&]+)') != '':
                final_url = re_me(dag_url, '&ver_t=([^&]+)&') + '?wmsAuthSign=' + re_me(dag_url, 'wmsAuthSign%3D([^%&]+)') + '==/mp4:' + re_me(dag_url, '\\?y=([^&]+)&')
            else:
                final_url = re_me(dag_url, 'href="([^"]+)"[^"]+$')
                if len(final_url)==0:
                    final_url=dag_url

            final_url = final_url.replace(' ', '%20')
            
        if '127.0.0.1' in dag_url:
            final_url = re_me(dag_url, '&ver_t=([^&]+)&') + ' live=true timeout=15 playpath=' + re_me(dag_url, '\\?y=([a-zA-Z0-9-_\\.@]+)')
        if re_me(dag_url, 'token=([^&]+)&') != '':
            final_url = final_url + '?token=' + re_me(dag_url, 'token=([^&]+)&')
            
        if 'jadoolive.elasticbeanstalk.com' in final_url:
            progress = xbmcgui.DialogProgress()
            progress.create('Progress', 'Fetching Streaming Info')
            progress.update( 10, "", "Finding Link..", "" )
            final_url=get_elastic_url(final_url)            

    # END Jadoo Link
    item.setProperty('streamLink', final_url)
    modelMap['live_item'] = item
    
def get_elastic_url(page_data):   
    page_data2=getUrl(page_data);
    patt='(http.*)'
    if 'adsid=' in page_data2:
        page_data=re.compile(patt).findall(page_data2)[0]
        page_data2=getUrl(page_data);
    else:
        return page_data

    import uuid
    playback=str(uuid.uuid1()).upper()
    links=re.compile(patt).findall(page_data2)
    headers=[('X-Playback-Session-Id',playback)]
    for l in links:
        try:
                page_datatemp=getUrl(l,headers=headers);
        except: traceback.print_exc(file=sys.stdout)

    return page_data+'|&X-Playback-Session-Id='+playback

def getUrl(url, cookieJar=None,post=None, timeout=20, headers=None):
    cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
    opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    if headers:
        for h,hv in headers:
            req.add_header(h,hv)

    response = opener.open(req,post,timeout=timeout)
    link=response.read()
    response.close()
    return link;
    
def _prepare_tv_show_items_(tv_shows, channel_type, channel_name, selected_tv_show_name, tv_show_items, is_finished_shows, modelMap, index):
    for tv_show in tv_shows:
        name = tv_show['name']
        if is_finished_shows:
            name = name + ' [COLOR gray]finished[/COLOR]'
        item = xbmcgui.ListItem(label=name)
        item.setProperty('channel-type', channel_type)
        item.setProperty('channel-name', channel_name)
        item.setProperty('tv-show-name', name)
        if is_finished_shows:
            item.setProperty('tv-show-finished', 'true')
        else:
            item.setProperty('tv-show-finished', 'false')
        item.setProperty('tv-show-url', tv_show['url'])
        tv_show_items.append(item)
        if selected_tv_show_name == name:
            modelMap['selected_tv_show_item'] = index
        index = index + 1
    return index

def empty_function(req_attrib, modelMap):
    return

def add_tv_show_favorite(req_attrib, modelMap):
    logging.getLogger().debug('add tv show favorite...')
    tv_show_url = req_attrib['tv-show-url']
    tv_show_name = req_attrib['tv-show-name']
    tv_show_thumb = req_attrib['tv-show-thumb']
    channel_type = req_attrib['channel-type']
    channel_name = req_attrib['channel-name']
    logging.getLogger().debug('add tv show favorite...' + tv_show_url)
    
    favorites = CacheManager().get('tv_favorites')
    if favorites is None:
        favorites = {}
    elif favorites.has_key(tv_show_name):
        favorites.pop(tv_show_name)
    
    favorites[tv_show_name] = {'tv-show-name':tv_show_name, 'tv-show-thumb':tv_show_thumb, 'tv-show-url':tv_show_url, 'channel-name':channel_name, 'channel-type':channel_type}
    context = AddonContext()
    filepath = file.resolve_file_path(context.get_addon_data_path(), extraDirPath='data', filename='DR_Favorites.json', makeDirs=False)
    logging.getLogger().debug(favorites)
    _write_favorite_tv_shows_cache_(filepath, favorites)
    
    notification = "XBMC.Notification(%s,%s,%s,%s)" % (tv_show_name, 'ADDED TO FAVORITES', 2500, tv_show_thumb)
    xbmc.executebuiltin(notification)
    
def load_remove_tv_show_favorite(req_attrib, modelMap):
    logging.getLogger().debug('load remove tv show favorite...')
    modelMap['tv-show-name'] = req_attrib['tv-show-name']
    modelMap['tv-show-thumb'] = req_attrib['tv-show-thumb']
    logging.getLogger().debug('display remove tv show favorite...')

    
def remove_favorite(req_attrib, modelMap):
    logging.getLogger().debug('remove tv show favorite...')
    favorite = CacheManager().get('selected_favorite')
    favorite_thumb = CacheManager().get('selected_favorite_thumb')
    favorites = CacheManager().get('tv_favorites')
    if favorites is None:
        favorites = {}
    elif favorites.has_key(favorite):
        favorites.pop(favorite)
    
    context = AddonContext()
    filepath = file.resolve_file_path(context.get_addon_data_path(), extraDirPath='data', filename='DR_Favorites.json', makeDirs=False)
    logging.getLogger().debug(favorites)
    _write_favorite_tv_shows_cache_(filepath, favorites)
    
    notification = "XBMC.Notification(%s,%s,%s,%s)" % (favorite, 'REMOVED FAVORITE', 2500, favorite_thumb)
    xbmc.executebuiltin(notification)
    
    modelMap['reload_favorite_tv_shows_items'] = True
    if len(favorites) > 0:
        favorite_tv_shows_items = []
        for tv_show_name in favorites:
            favorite_tv_show = favorites[tv_show_name]
            item = xbmcgui.ListItem(label=tv_show_name, iconImage=favorite_tv_show['tv-show-thumb'], thumbnailImage=favorite_tv_show['tv-show-thumb'])
            item.setProperty('channel-type', favorite_tv_show['channel-type'])
            item.setProperty('channel-name', favorite_tv_show['channel-name'])
            item.setProperty('tv-show-name', tv_show_name)
            item.setProperty('tv-show-url', favorite_tv_show['tv-show-url'])
            item.setProperty('tv-show-thumb', favorite_tv_show['tv-show-thumb'])
            favorite_tv_shows_items.append(item)
            
        modelMap['favorite_tv_shows_items'] = favorite_tv_shows_items
    
    
def load_tv_show_episodes(req_attrib, modelMap):
    logging.getLogger().debug('load tv show episodes...')
    url = req_attrib['tv-show-url']
    tv_show_url = req_attrib['tv-show-url']
    tv_show_name = req_attrib['tv-show-name']
    channel_type = req_attrib['channel-type']
    channel_name = req_attrib['channel-name']
    currentPage = 1
    
    if req_attrib.has_key('tv-show-page') and req_attrib['tv-show-page'] != '':
        currentPage = int(req_attrib['tv-show-page'])
        if currentPage != 1:
            url = url + '/page' + req_attrib['tv-show-page']
    logging.getLogger().debug('load tv show episodes...' + url)
    soup = BeautifulSoup.BeautifulSoup(HttpClient().get_html_content(url=url)).findAll('div', {'id':'contentBody'})[0]
    
    tv_show_episode_items = []
    if currentPage == 1:
        logging.getLogger().debug('get sticky threads for current page : %s' % str(currentPage))
        threads = soup.find('ol', {'class':'stickies', 'id':'stickies'})
        tv_show_episode_items.extend(__retrieveTVShowEpisodes__(threads, tv_show_name, channel_type, channel_name))
    
    threads = soup.find('ol', {'class':'threads', 'id':'threads'})
    tv_show_episode_items.extend(__retrieveTVShowEpisodes__(threads, tv_show_name, channel_type, channel_name))
    logging.getLogger().debug('In DR: total tv show episodes: %s' % str(len(tv_show_episode_items)))
    
    pagesDiv = soup.find('div', {'class':'threadpagenav'})
    if pagesDiv is not None:
        pagesInfoTag = pagesDiv.find('a', {'class':re.compile(r'\bpopupctrl\b')})
        if pagesInfoTag is not None:
            pageInfo = re.compile('Page (.+?) of (.+?) ').findall(pagesInfoTag.getText() + ' ')
            totalPages = int(pageInfo[0][1])
            for page in range(1, totalPages + 1):
                if page != currentPage:
                    pageName = ''
                    if page < currentPage:
                        pageName = '[B]     <-    Page #' + str(page) + '[/B]'
                    else:
                        pageName = '[B]     ->    Page #' + str(page) + '[/B]'
                    
                    item = xbmcgui.ListItem(label=pageName)
                    item.setProperty('channel-type', channel_type)
                    item.setProperty('channel-name', channel_name)
                    item.setProperty('tv-show-name', tv_show_name)
                    item.setProperty('tv-show-url', tv_show_url)
                    if page != 1:
                        item.setProperty('tv-show-page', str(page))
                    tv_show_episode_items.append(item)
    
    modelMap['tv_show_episode_items'] = tv_show_episode_items
    

def __retrieveTVShowEpisodes__(threads, tv_show_name, channel_type, channel_name):
    tv_show_episode_items = []
    logging.getLogger().debug(threads)
    if threads is None:
        return []
    aTags = threads.findAll('a', {'class':re.compile(r'\btitle\b')})
    logging.getLogger().debug(aTags)
    videoEpisodes = []
    for aTag in aTags:
        episodeName = aTag.getText()
        if not re.search(r'\b(Watch|Episode|Video|Promo)\b', episodeName, re.IGNORECASE):
            pass
        else:
            videoEpisodes.append(aTag)
            
    if len(videoEpisodes) == 0:
        videoEpisodes = aTags
        
    for aTag in videoEpisodes:
        episodeName = aTag.getText()
        titleInfo = http.unescape(episodeName)
        titleInfo = titleInfo.replace(tv_show_name, '')
        titleInfo = titleInfo.replace(' - Video Watch Online', '')
        titleInfo = titleInfo.replace(' - Video Watch online', '')
        titleInfo = titleInfo.replace('Video Watch Online', '')
        titleInfo = titleInfo.replace('Video Watch online', '')
        titleInfo = titleInfo.replace('Watch Online', '')
        titleInfo = titleInfo.replace('Watch online', '')
        titleInfo = titleInfo.replace('Watch', '')      
        titleInfo = titleInfo.replace('Video', '')
        titleInfo = titleInfo.replace('video', '')
        titleInfo = titleInfo.replace('-', '')
        titleInfo = titleInfo.replace('/ Download', '')
        titleInfo = titleInfo.replace('/Download', '')
        titleInfo = titleInfo.replace('Download', '')
        titleInfo = titleInfo.strip()
        
        item = xbmcgui.ListItem(label=titleInfo)
        
        episode_url = str(aTag['href'])
        if not episode_url.lower().startswith(BASE_WSITE_URL):
            if episode_url[0] != '/':
                episode_url = '/' + episode_url
            episode_url = BASE_WSITE_URL + episode_url
        item.setProperty('tv-show-name', tv_show_name)
        item.setProperty('channel-type', channel_type)
        item.setProperty('channel-name', channel_name)
        item.setProperty('episode-name', titleInfo)
        item.setProperty('episode-url', episode_url)
        tv_show_episode_items.append(item)
        
    return tv_show_episode_items


def determine_tv_show_episode_videos(req_attrib, modelMap):
    logging.getLogger().debug('determine tv show episode videos...')
    if req_attrib['episode-url'] is None or req_attrib['episode-url'] == '':
        return 'redirect:dr-displayShowEpisodesList'

def load_tv_show_episode_videos(req_attrib, modelMap):
    logging.getLogger().debug('load tv show episode videos...')
    list_items = _retrieve_video_links_(req_attrib, modelMap)
    
    ''' Following new cool stuff is to get Smart Direct Play Feature'''
    playNowItem = __findPlayNowStream__(list_items)
    logging.getLogger().debug('found play now stream... ')
    modelMap['selected-playlist-item'] = playNowItem['selected']
    modelMap['backup-playlist-item'] = playNowItem['backup']
    
def load_tv_show_episode_videos_list(req_attrib, modelMap):
    logging.getLogger().debug('load tv show episode videos list...')
    list_items = _retrieve_video_links_(req_attrib, modelMap)
    modelMap['videos-item-list'] = list_items

def load_selected_playlist_streams(req_attrib, modelMap):
    selected_playlist_item = modelMap['selected-playlist-item']
    video_items = None
    if selected_playlist_item is not None:
        selected_playlist = selected_playlist_item.getProperty('videoPlayListItemsKey')
        logging.getLogger().debug('load selected playlist streams... %s' % selected_playlist)
        playlist_items = modelMap[selected_playlist]
        try:
            video_items = _retrieve_playlist_streams_(modelMap['progress_control'], playlist_items)
        except:
            modelMap['progress_control'].setPercent(0)
            pass
    if video_items is None:
        backup_playlist_item = modelMap['backup-playlist-item']
        backup_playlist = backup_playlist_item.getProperty('videoPlayListItemsKey')
        logging.getLogger().debug('load backup playlist streams... %s' % backup_playlist)
        playlist_items = modelMap[backup_playlist]
        video_items = _retrieve_playlist_streams_(modelMap['progress_control'], playlist_items)
    
    modelMap['video_streams'] = video_items
    
    
def _retrieve_playlist_streams_(progress_bar, playlist_items):
    lazyLoadStream = AddonContext().get_addon().getSetting('drLazyLoadStream')
    current_index = 1
    total_iteration = len(playlist_items)
    video_items = []
    for item in playlist_items:
        logging.getLogger().debug('About to retrieve video link %s' % item)
        video_item = None
        if lazyLoadStream is None or lazyLoadStream == 'false':
            video_item = SnapVideo().resolveVideoStream(item['videoLink'])
        else:
            video_item = _create_video_stream_item(item['videoLink'], str(current_index))
        video_items.append(video_item)
        percent = (current_index * 100) / total_iteration
        progress_bar.setPercent(percent)
        current_index = current_index + 1
    return video_items


def load_selected_video_playlist_streams(req_attrib, modelMap):
    progress_bar = req_attrib['progress_control']
    progress_bar.setPercent(0)
    video_items = None
    if req_attrib['is-playlist'] == 'true':
        playlist_items = pickle.loads(req_attrib['videos'])
        video_items = _retrieve_playlist_streams_(progress_bar, playlist_items)
    else:
        video_items = []
        video_item = SnapVideo().resolveVideoStream(req_attrib['video-link'])
        video_items.append(video_item)
        progress_bar.setPercent(100)
    modelMap['video_streams'] = video_items
    
    
def _create_video_stream_item(videoLink, inx=''):
    videoHostingInfo = SnapVideo().findVideoHostingInfo(videoLink)
    label = videoHostingInfo.get_name() + inx
    item = xbmcgui.ListItem(label=label, iconImage=videoHostingInfo.get_icon(), thumbnailImage=videoHostingInfo.get_icon())
    item.setProperty('streamLink', 'plugin://plugin.video.zeritv/?videoLink=' + urllib.quote_plus(videoLink))
    return item


def _read_tv_channels_cache_(filepath):
    tv_data = CacheManager().get('tv_data')
    if tv_data is None:
        tv_data = jsonfile.read_file(filepath)
        CacheManager().put('tv_data', tv_data)
    return tv_data


def _read_favorite_tv_shows_cache_(filepath):
    favorites = CacheManager().get('tv_favorites')
    if favorites is None:
        favorites = jsonfile.read_file(filepath)
        CacheManager().put('tv_favorites', favorites)
    return favorites

def _write_favorite_tv_shows_cache_(filepath, data):
    CacheManager().put('tv_favorites', data)
    jsonfile.write_file(filepath, data)


def __retrieve_tv_shows__(tv_channel_url):
    logging.getLogger().debug(tv_channel_url)
    tv_shows = []
    if tv_channel_url is None:
        return tv_shows
    tv_channel_url = BASE_WSITE_URL + tv_channel_url
    logging.getLogger().debug(tv_channel_url)
    soup = BeautifulSoup.BeautifulSoup(HttpClient().get_html_content(url=tv_channel_url)).findAll('div', {'id':'forumbits', 'class':'forumbits'})[0]
    for title_tag in soup.findAll('h2', {'class':'forumtitle'}):
        aTag = title_tag.find('a')
        tv_show_url = str(aTag['href'])
        if tv_show_url[0:4] != "http":
            tv_show_url = BASE_WSITE_URL + '/' + tv_show_url
        tv_show_name = aTag.getText()
        if not re.search('Past Shows', tv_show_name, re.IGNORECASE):
            tv_shows.append({"name":http.unescape(tv_show_name), "url":tv_show_url, "iconimage":""})
    return tv_shows
    
    
def __retrieve_channel_tv_shows__(tv_channel_name, tv_channel):
    running_tvshows = []
    finished_tvshows = []
    try:
        running_tvshows = __retrieve_tv_shows__(tv_channel["running_tvshows_url"])
        if(len(running_tvshows) == 0):
            running_tvshows.append({"name":"ERROR: UNABLE TO LOAD. Share message on http://forum.xbmc.org/showthread.php?tid=115583", "url":BASE_WSITE_URL + tv_channel["running_tvshows_url"]})
    except Exception, e:
        logging.getLogger().exception(e)
        logging.getLogger().debug('Failed to load a channel <%s>. continue retrieval of next tv show' % tv_channel_name)
    try:
        finished_tvshows = __retrieve_tv_shows__(tv_channel["finished_tvshows_url"])
    except Exception, e:
        logging.getLogger().exception(e)
        logging.getLogger().debug('Failed to load a channel <%s>. continue retrieval of next tv show' % tv_channel_name)
    tv_channel["running_tvshows"] = running_tvshows
    tv_channel["finished_tvshows"] = finished_tvshows


def _retrieve_video_links_(req_attrib, modelMap):
    
    modelMap['channel-name'] = req_attrib['channel-name']
    modelMap['tv-show-name'] = req_attrib['tv-show-name']
    modelMap['episode-name'] = req_attrib['episode-name']
    
    video_source_id = 1
    video_source_img = None
    video_source_name = None
    video_part_index = 0
    video_playlist_items = []
    ignoreAllLinks = False
    
    list_items = []
    
    soup = BeautifulSoup.BeautifulSoup(HttpClient().get_html_content(url=req_attrib['episode-url'])).findAll('blockquote', {'class':re.compile(r'\bpostcontent\b')})[0]
    
    for e in soup.findAll('br'):
        e.extract()
    
    # Removing the child font within font to handle where the font gets changed at the end for HQ    
    for e in soup.find('font').findAll('font'):
        e.extract()    
    
    logging.getLogger().debug(soup)
    if soup.has_key('div'):
        soup = soup.findChild('div', recursive=False)
    prevChild = ''
    prevAFont = None
    isHD = 'false'
    videoSource = ''
    for child in soup.findChildren():
        if (child.name == 'img' or child.name == 'b' or (child.name == 'font' and not child.findChild('a'))):
            if (child.name == 'b' and prevChild == 'a') or (child.name == 'font' and child == prevAFont):
                continue
            else:
                if len(video_playlist_items) > 0:
                    list_items.append(__preparePlayListItem__(video_source_id, video_source_img, video_source_name, video_playlist_items, modelMap, isHD))
                
                logging.getLogger().debug(videoSource)
                videoSource = child.getText()
                if(re.search('720p', videoSource, re.I)):
                    isHD = 'true'
                else:
                    isHD = 'false'
                if video_source_img is not None:
                    video_source_id = video_source_id + 1
                    video_source_img = None
                    video_source_name = None
                    video_part_index = 0
                    video_playlist_items = []
                ignoreAllLinks = False
        elif not ignoreAllLinks and child.name == 'a' and not re.search('multi', str(child['href']), re.IGNORECASE):
            video_part_index = video_part_index + 1
            video_link = {}
            video_link['videoTitle'] = 'Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) + ' | ' + child.getText()
            video_link['videoLink'] = str(child['href'])
            video_link['videoSource'] = videoSource
            try:
                try:
                    __prepareVideoLink__(video_link)
                except Exception, e:
                    logging.getLogger().error(e)
                    video_hosting_info = SnapVideo().findVideoHostingInfo(video_link['videoLink'])
                    if video_hosting_info is None or video_hosting_info.get_name() == 'UrlResolver by t0mm0':
                        raise
                    video_link['videoSourceImg'] = video_hosting_info.get_icon()
                    video_link['videoSourceName'] = video_hosting_info.get_name()
                video_playlist_items.append(video_link)
                video_source_img = video_link['videoSourceImg']
                video_source_name = video_link['videoSourceName']
                
                item = xbmcgui.ListItem(label='Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) , iconImage=video_source_img, thumbnailImage=video_source_img)
                item.setProperty('videoLink', video_link['videoLink'])
                item.setProperty('videoTitle', video_link['videoTitle'])
                item.setProperty('videoSourceName', video_source_name)
                item.setProperty('isContinuousPlayItem', 'false')
                list_items.append(item)
                
                prevAFont = child.findChild('font')
            except:
                logging.getLogger().error('Unable to recognize a source = ' + str(video_link['videoLink']))
                video_source_img = None
                video_source_name = None
                video_part_index = 0
                video_playlist_items = []
                ignoreAllLinks = True
                prevAFont = None
        prevChild = child.name
    if len(video_playlist_items) > 0:
        list_items.append(__preparePlayListItem__(video_source_id, video_source_img, video_source_name, video_playlist_items, modelMap, isHD))
    return list_items


def __preparePlayListItem__(video_source_id, video_source_img, video_source_name, video_playlist_items, modelMap, isHD):
    item = xbmcgui.ListItem(label='[B]Continuous Play[/B]' + ' | ' + 'Source #' + str(video_source_id) + ' | ' + 'Parts = ' + str(len(video_playlist_items)) , iconImage=video_source_img, thumbnailImage=video_source_img)
    item.setProperty('videoSourceName', video_source_name)
    item.setProperty('isContinuousPlayItem', 'true')
    item.setProperty('isHD', isHD)
    item.setProperty('videoPlayListItemsKey', 'playlist#' + str(video_source_id))
    item.setProperty('videosList', pickle.dumps(video_playlist_items))
    modelMap['playlist#' + str(video_source_id)] = video_playlist_items
    return item


def __prepareVideoLink__(video_link):
    logging.getLogger().debug(video_link)
    video_url = video_link['videoLink']
    video_source = video_link['videoSource']
    new_video_url = None
    if re.search('videos.desihome.info', video_url, flags=re.I):
        new_video_url = __parseDesiHomeUrl__(video_url)
    if new_video_url is None:        
        
        video_id = re.compile('(id|url|v|si)=(.+?)/').findall(video_url + '/')[0][1]                
        
        if re.search('dm(\d*).php', video_url, flags=re.I) or ((re.search('(desiserials|serialreview|tellyserials|[a-z]*).tv/', video_url, flags=re.I) or re.search('bigbangreviews.com/|tvnewz.net/|reviewxpress.net/', video_url, flags=re.I)) and not video_id.isdigit() and re.search('dailymotion', video_source, flags=re.I)):
            new_video_url = 'http://www.dailymotion.com/video/' + video_id + '_'                        
        elif re.search('(flash.php|fp.php|wire.php|pw.php)', video_url, flags=re.I) or ((re.search('(desiserials|serialreview|tellyserials|[a-z]*).tv/', video_url, flags=re.I) or re.search('bigbangreviews.com/|tvnewz.net/|reviewxpress.net/', video_url, flags=re.I)) and video_id.isdigit() and re.search('flash', video_source, flags=re.I)):
            new_video_url = 'http://config.playwire.com/videos/v2/' + video_id + '/player.json'            
        elif re.search('(youtube|u|yt)(\d*).php', video_url, flags=re.I):
            new_video_url = 'http://www.youtube.com/watch?v=' + video_id + '&'
        elif re.search('mega.co.nz', video_url, flags=re.I):
            new_video_url = video_url
        elif re.search('(put|pl).php', video_url, flags=re.I):
            new_video_url = 'http://www.putlocker.com/file/' + video_id
        elif re.search('cloud.php', video_url, flags=re.I):
            new_video_url = 'http://www.cloudy.ec/embed.php?id=' + video_id
        elif re.search('videohut.php', video_url, flags=re.I) or ((re.search('(desiserials|serialreview|tellyserials|[a-z]*).tv/', video_url, flags=re.I) or re.search('bigbangreviews.com/|tvnewz.net/|reviewxpress.net/', video_url, flags=re.I)) and not video_id.isdigit() and re.search('video hut', video_source, flags=re.I)):
            new_video_url = 'http://www.videohut.to/embed.php?id=' + video_id                        
        elif re.search('(weed.php|vw.php)', video_url, flags=re.I):
            new_video_url = 'http://www.videoweed.es/file/' + video_id
        elif re.search('(sockshare.com|sock.com)', video_url, flags=re.I):
            new_video_url = video_url
        elif re.search('divxstage.php', video_url, flags=re.I):
            new_video_url = 'divxstage.eu/video/' + video_id + '&'
        elif re.search('(hostingbulk|hb).php', video_url, flags=re.I):
            new_video_url = 'hostingbulk.com/' + video_id + '&'
        elif re.search('(movshare|ms).php', video_url, flags=re.I):
            new_video_url = 'movshare.net/video/' + video_id + '&'
        elif re.search('mz.php', video_url, flags=re.I):
            new_video_url = 'movzap.com/' + video_id + '&'
        elif re.search('nv.php', video_url, flags=re.I):
            new_video_url = 'nowvideo.ch/embed.php?v=' + video_id + '&'
        elif re.search('nm.php', video_url, flags=re.I):
            new_video_url = 'novamov.com/video/' + video_id + '&'
        elif re.search('tune.php', video_url, flags=re.I) or ((re.search('(desiserials|serialreview|tellyserials|[a-z]*).tv/', video_url, flags=re.I) or re.search('bigbangreviews.com/|tvnewz.net/|reviewxpress.net/', video_url, flags=re.I)) and video_id.isdigit() and re.search('tune.pk', video_source, flags=re.I)):
            new_video_url = 'tune.pk/play/' + video_id + '&'
        elif re.search('vshare.php', video_url, flags=re.I):
            new_video_url = 'http://vshare.io/d/' + video_id + '&'
        elif re.search('vidto.php', video_url, flags=re.I):
            new_video_url = 'http://vidto.me/' + video_id + '.html'
        elif re.search('videotanker.php', video_url, flags=re.I) or ((re.search('(desiserials|serialreview|tellyserials|[a-z]*).tv/', video_url, flags=re.I) or re.search('bigbangreviews.com/|tvnewz.net/|reviewxpress.net/', video_url, flags=re.I)) and video_id.isdigit() and re.search('video tanker', video_source, flags=re.I)):
            new_video_url = 'http://videotanker.co/player/embed_player.php?vid=' + video_id + '&'

    
    video_hosting_info = SnapVideo().findVideoHostingInfo(new_video_url)
    video_link['videoLink'] = new_video_url
    video_link['videoSourceImg'] = video_hosting_info.get_icon()
    video_link['videoSourceName'] = video_hosting_info.get_name()



def __parseDesiHomeUrl__(video_url):
    video_link = None
    logging.getLogger().debug('video_url = ' + video_url)
    html = HttpClient().get_html_content(url=video_url)
    if re.search('dailymotion.com', html, flags=re.I):
        video_link = 'http://www.dailymotion.com/' + re.compile('dailymotion.com/(.+?)"').findall(html)[0] + '&'
    elif re.search('hostingbulk.com', html, flags=re.I):
        video_link = 'http://hostingbulk.com/' + re.compile('hostingbulk.com/(.+?)"').findall(html)[0] + '&'
    elif re.search('movzap.com', html, flags=re.I):
        video_link = 'http://movzap.com/' + re.compile('movzap.com/(.+?)"').findall(html)[0] + '&'
    return video_link


PREFERRED_DIRECT_PLAY_ORDER = [Dailymotion.VIDEO_HOSTING_NAME, Playwire.VIDEO_HOSTING_NAME, VideoWeed.VIDEO_HOST_NAME, CloudEC.VIDEO_HOST_NAME, Tune_pk.VIDEO_HOSTING_NAME, YouTube.VIDEO_HOSTING_NAME, Nowvideo.VIDEO_HOST_NAME, Novamov.VIDEO_HOST_NAME]

def __findPlayNowStream__(new_items):
#     if AddonContext().get_addon().getSetting('autoplayback') == 'false':
#         return None
    logging.getLogger().debug('FINDING the source..')
    selectedIndex = None
    selectedSource = None
    hdSelected = False
    backupSource = None
    backupSourceName = None
    for item in new_items:
        if item.getProperty('isContinuousPlayItem') == 'true':
            source_name = item.getProperty('videoSourceName')
            try:
                logging.getLogger().debug(source_name)
                preference = PREFERRED_DIRECT_PLAY_ORDER.index(item.getProperty('videoSourceName'))
                if preference == 0 and (selectedIndex is None or selectedIndex != 0) and not hdSelected :
                    selectedSource = item
                    selectedIndex = 0
                elif selectedIndex is None or selectedIndex > preference:
                    selectedSource = item
                    selectedIndex = preference
                if item.getProperty('isHD') == 'true' and selectedIndex is not None:
                    hdSelected = True
                    
                if ((source_name == CloudEC.VIDEO_HOST_NAME or source_name == Playwire.VIDEO_HOSTING_NAME) and backupSource is None):
                    logging.getLogger().debug("Added to backup plan: %s" % source_name)
                    backupSource = item
                    backupSourceName = source_name
                    
            except ValueError:
                logging.getLogger().debug("Exception for source : %s" % source_name)
                if source_name == CloudEC.VIDEO_HOST_NAME and (backupSource is None or backupSourceName != CloudEC.VIDEO_HOST_NAME):
                    logging.getLogger().debug("Added to backup plan: %s" % source_name)
                    backupSource = item
                    backupSourceName = source_name
                elif backupSource is None:
                    logging.getLogger().debug("Added to backup plan when Playwire not found: %s" % source_name)
                    backupSource = item
                    backupSourceName = source_name
                continue
    sources = {}
    sources['selected'] = selectedSource
    sources['backup'] = backupSource
    return sources

