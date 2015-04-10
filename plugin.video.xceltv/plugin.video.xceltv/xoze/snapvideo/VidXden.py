'''
Created on Feb 1, 2015

@author: jchirag
'''
from xoze.snapvideo import VideoHost, UrlResolverDelegator

def getVideoHost():
    video_host = VideoHost()
    video_host.set_icon('')
    video_host.set_name('VidXden')
    return video_host

def retrieveVideoInfo(video_id):
    videoUrl = 'http://www.vidxden.com/' + str(video_id)
    return UrlResolverDelegator.retrieveVideoInfo(videoUrl)
