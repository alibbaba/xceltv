'''
Created on Feb 1, 2015

@author: jchirag
'''
from xoze.snapvideo import VideoHost, UrlResolverDelegator
    
def getVideoHost():
    video_host = VideoHost()
    video_host.set_icon('http://www.vidbux.com/images/vid_bux_logo_small.png')
    video_host.set_name('VidBux')
    return video_host
    
def retrieveVideoInfo(video_id):
    videoUrl = 'http://www.vidbux.com/' + str(video_id)
    return UrlResolverDelegator.retrieveVideoInfo(videoUrl)

