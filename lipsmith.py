from __future__ import unicode_literals
import youtube_dl

import sys
import os
import subprocess
import argparse
import glob

import json
from collections import OrderedDict
import io

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

if sys.platform == "win32":
    FFMPEG_BIN = "ffmpeg.exe"
    MOVE = "move "
    MKDIR = "md "
elif sys.platform == 'linux' or sys.platform == 'linux2':
    FFMPEG_BIN = "ffmpeg"
    MOVE = "mv "
    MKDIR = "mkdir "
elif sys.platform == 'darwin':
    FFMPEG_BIN = "ffmpeg"
    MOVE = "mv "
    MKDIR = "mkdir "

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def listToStringWithoutBrackets(list1):
    return str(list1).replace('[','').replace(']','')

def iframe_extract(jsonFile, audioFile):
# ffmpeg -i inFile -f image2 -vf \
#   "select='eq(pict_type,PICT_TYPE_I)'" -vsync vfr oString%03d.png

    # infile : video file name 
    #          (ex) 'FoxSnowDive-Yellowstone-BBCTwo.mp4'
    
    #imgPrefix = inFile.split('.')[0]
    # imgPrefix : image file 
    #imgFilenames = imgPrefix + '%03d.png'
    
    # start extracting i-frames
    # home = os.path.expanduser("~")
    home = os.path.dirname(os.path.realpath(__file__))
    # ffmpeg = home + '/bin/ffmpeg'
    rhubarb = home + '/rhubarb/rhubarb'
    audioFile = audioFile
    
    #cmd = [ffmpeg,'-i', inFile,'-f', 'image2','-vf', "select='eq(pict_type,PICT_TYPE_I)'",'-vsync','vfr', imgFilenames]
    cmd = [rhubarb, '-f', 'json', audioFile]

    # create iframes
    print("creating iframes ....")
    output = subprocess.check_output(cmd)
    data = json.loads(output)

    '''
    with open('skeleton.json', 'r') as skeleton:
        ### SAM: spineData instead of spineFile
        spineFile = skeleton.read().split('"animations": {')
    ''' 

    with open(jsonFile) as json_data:
        d = json.load(json_data, object_pairs_hook=OrderedDict)

    ### SAM: create new array to hold cues / keyframe info that spine can understand
    newCues = []
    for idx, item in enumerate(data['mouthCues']):
        #newCueData = json.dumps({"time": item['start'], "name": item['value']}, sort_keys=False)
        newCueData = '{"time": ' + str(item['start']) + ', ' + '"name": "lips_' + item['value'] + '" }'
        ''' SAM: following 2 lines are redunant
        #newCueData = json.loads(newCueData, object_pairs_hook=OrderedDict)
        #newCues.append(json.dumps(newCueData))
        '''
        newCues.append(newCueData)
        #print _byteify(item)

    #print newCues
    if d['animations']:
        x = ''
        for idx, item in enumerate(newCues):
            if x:
                x += ',\n'
            ### SAM: json.loads() with object_pairs_hook=OrderedDict
            data = json.loads(item, object_pairs_hook=OrderedDict)
            data = json.dumps(data, sort_keys=False, indent=4)
            x += data
        cues = '{"animation":{"slots":{"lips":{"attachment":['+x+']}}}}'
        d['animations'] = json.loads(cues, object_pairs_hook=OrderedDict)

    ### SAM: insert mouthCues into existing spineFile (skeleton.json)
    '''
    if len(spineFile) == 2:
        hierarchy = '"animations":{"animation":{"slots":{"out/A":{"attachment":['
        mouthCues = hierarchy + ', '.join(newCues) + ']}}}}'
        mouthCuesDecoded = json.JSONDecoder().decode('["foo", {"bar":["baz", null, 1.0, 2]}]')
        #print json.dumps(mouthCuesDecoded, indent=4)
        a = json.dumps(json.loads('{"4": 5, "6": 7}'), indent=4)
        #print a
        bCues = '{"animations":{"animation":{}}}'
        b = json.dumps(json.loads(bCues), indent=4)
        #print b
        #spineFile.insert(1, json.loads(json.dumps(mouthCuesDecoded, indent=4)))    
    '''    

    #newData = json.loads(spineFile)
    #j = json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')

    '''
    for idx, item in enumerate(spineFile):
        print idx
        print _byteify(item)
    '''

    with io.open(jsonFile, 'w', encoding='utf8') as outfile:
        ### SAM: stuff
        #outfile.write(to_unicode(str_))
        #data = json.dumps(d, ensure_ascii=False, encoding='utf8').encode('utf8')
        #strTest_ = json.loads(json.dumps('["foo", {"bar":["baz", null, 1.0, 2]}]', indent=4, separators=(',', ':'), ensure_ascii=False))
        #str_ = json.loads(json.dumps(''.join(spineFile), indent=4, separators=(',', ':'), ensure_ascii=False))
        str_ = to_unicode(json.dumps(d, indent=4, skipkeys=True))
        #str_e = to_unicode(json.dumps(e, indent=4, skipkeys=True))
        outfile.write(str_)

    '''
    # Move the extracted iframes to a subfolder
    # imgPrefix is used as a subfolder name that stores iframe images
    cmd = MKDIR + '-p ' + imgPrefix
    os.system(cmd)
    print("make subdirectoy=%s" %cmd)
    mvcmd = MOVE + imgPrefix + '*.png ' + imgPrefix
    print("moving images to subdirectoy %s" %mvcmd)
    os.system(mvcmd)
    '''

'''
def get_info_and_download(download_url):

    # Get video meta info and then download using youtube-dl

    ydl_opts = {}

    # get meta info from the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(download_url, download=False)

    # renaming the file 
    # remove special characters from the file name
    print('meta[title]=%s' %meta['title'])
    out = ''.join(c for c in meta['title'] if c.isalnum() or c =='-' or c =='_' ) 
    print('out=%s' %out)
    extension = meta['ext']
    video_out = out + '.' + extension
    print('video_out=%s' %video_out)
    videoSize = 'bestvideo[height<=540]+bestaudio/best[height<=540]'
    cmd = ['youtube-dl', '-f', videoSize, '-k', '-o', video_out, download_url]
    print('cmd=%s' %cmd)

    # download the video
    subprocess.call(cmd)

    # Sometimes output file has format code in name such as 'out.webm'
    # So, when the best output format happens to be mp4, for example, 'out.webm.mp4' 
    # which is the input file for iframe_extract(). But there is no 'out.webm.mp4' any more.
    # The following will reset the input as the newly merged video output, 'out.webm.mp4' 
    found = False
    extension_list = ['mkv', 'mp4', 'webm']
    for e in extension_list:
       glob_str = '*.' + e
       for f in glob.glob(glob_str):
          if out in f:
             if os.path.isfile(f):
                video_out = f
                found = True
                break
       if found:
          break
       
    # call iframe-extraction : ffmpeg
    print('before iframe_extract() video_out=%s' %video_out)
    iframe_extract(video_out)
    return meta
'''


def check_arg(args=None):

# Command line options
# Currently, only the url option is used

    parser = argparse.ArgumentParser(description='download video')
    parser.add_argument('-j', '--json',
                        help='download url',
                        required='True')
    parser.add_argument('-a', '--audio',
                        help='input to iframe extract',
                        required='True')

    results = parser.parse_args(args)
    return (results.json,
            results.audio)


# Usage sample:
#    syntax: python iframe_extract.py -u url
#    (ex) python iframe_extract.py -u https://www.youtube.com/watch?v=dP15zlyra3c

if __name__ == '__main__':
    # json/skin, audio
    j, a = check_arg(sys.argv[1:])
    #meta = get_info_and_download(u)
    iframe_extract(j, a)
