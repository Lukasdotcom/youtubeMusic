#! /usr/bin/env python3
from pytube import YouTube, Playlist
import sys
import os
import json
import glob
import vlc
import random
import time
from threading import Thread
from mutagen.mp4 import MP4
print("youtubeMusic downloader is starting! This program can be used to download your music playlist from youtube for free in a fast and easy way!")
print("If this program is not working for you please put a issue on github. Many issues exist because of the library that this was built on so they may not be fixable temporarily.")

def writeFile(location, info):  # Will write info in json format to a file
    with open(location, 'w') as f:
        json.dump(info, f)


def readFile(location):  # Loads the location of a certain file and returns that file if it is json
    with open(location, "r") as f:
        try:
            return json.load(f)
        except:
            raise Exception(
                f"Json file at {location} has corrupted or invalid entries")


print("Searching for configuration files")
try:  # Will check for the arguments for the location of the config
    location = sys.argv[1]
    configLocation = location + ".config.json"
    cacheLocation = location + ".cache.json"
except:
    # Will find where the programs working directory is.
    print("argument missing for directory using working directory of program")
    location = str(os.getcwdb())[2:-1]
    # Will check if this is on windows
    if location[0] == "C":
        ending = "\\"
    else:
        ending = location[0]
    location = f"{location}{ending}"
    configLocation = location + ".config.json"
    cacheLocation = location + ".cache.json"
if not os.path.isdir(location):  # Will check if the folder for the config exists
    os.makedirs(location)
    print("Folder did not exist created new folder at" + location)
try:
    writeFile(configLocation + "temp", {})
    os.remove(configLocation + "temp")
except:
    print(f"Directory, {location} could not be accessed using {sys.path[0]}")
    location = sys.path[0]
    configLocation = location + ".config.json"
    cacheLocation = location + ".cache.json"
# Will find the config file and create a new one if it does not exist
if not os.path.isfile(configLocation):
    print("New folder detected creating new config")
    writeFile(configLocation, {})
    configInfo = {}
else:
    configInfo = readFile(configLocation)
    print("Found Configuration files")
if not os.path.isfile(cacheLocation):
    print("New folder detected creating new cache")
    writeFile(cacheLocation, {})
else:
    print("Found cache files")


def update(configInfo):  # updates all playlists
    global cacheLocation
    cacheInfo = readFile(cacheLocation)
    number = 1
    configLen = len(configInfo)
    for x in configInfo:
        try: # will check if the playlist is valid
            playlist = Playlist(x)
            print(
                f"Starting update of playlist {number} of {configLen} called {playlist.title} at location {configInfo[x]}")
        except:
            print(
                f"Skipping update of playlist {number} of {configLen} because of invalid link")
            number += 1
            break
        # Will check if the folder for the config exists
        if not os.path.isdir(configInfo[x]):
            os.makedirs(configInfo[x])
            print(
                f"Folder for {playlist.title} not exist created new folder at {configInfo[x]}")
        howFarVideo = 0 # Used to see how many videos the program is through
        videoLen = len(playlist.videos) # how many videos are in the playlist
        songList = glob.glob(configInfo[x] + "*.mp3") # a list of all songs already downloaded to make sure there are not extra songs that need to be deleted
        # goes through every video in the playlist
        for y in playlist.videos:
            try: # looks if the metadata is cached
                metadata = cacheInfo[y.watch_url]
                skip = True
            except:
                try: # looks if the metadata characteristic exists for a video
                    metadata = y.metadata.metadata[0]
                except:
                    metadata = {}
                skip = False # used to check if the cache needs to be updated
            try: # checks the title otherwise uses the title of the video
                videoTitle = metadata["Song"]
            except:
                try:
                    videoTitle = y.title
                    skip = False
                except:
                    print("cant find video title skipping")
                    continue
                print(f"Song title not found resorting to video title of {videoTitle}")
            bannedCharacters = [".", "'", '"', ",", "/", "\\", "?"] # invalid characters for file names
            videoTitle2 = ""
            for z in videoTitle: # removes banned characters from a video
                if z not in bannedCharacters:
                    videoTitle2 += z
            videoTitle = videoTitle2
            try: # Checks for the artist otherwise uses the name of the channel
                videoAuthor = metadata["Artist"]
            except:
                videoAuthor = y.author
                if videoAuthor[-7:] == "- Topic": # Channels for some reason have - Topic at the end so that is removed
                    videoAuthor = videoAuthor[:-8]
                skip = False
                print(f"Song artist not found using video channel name {videoAuthor}")
            videoAuthor2 = ""
            for z in videoAuthor: # removes banned characters from a video
                if z not in bannedCharacters:
                    videoAuthor2 += z
            videoAuthor = videoAuthor2
            try: # Checks if an album is in the metadata
                videoAlbum = metadata["Album"]
            except:
                skip = False
                videoAlbum = "unknown"
                print(f"Song album not found")
            howFarVideo += 1 
            # prints a status update
            print(
                f"Playlist {number} of {configLen}; Video {howFarVideo} of {videoLen} called {videoTitle}; ")
            name = configInfo[x] + videoTitle + ".mp4"
            if (configInfo[x] + videoTitle + ".mp3") in songList: # checks if the song was already downloaded
                songList.remove(configInfo[x] + videoTitle + ".mp3") # removes the song from the deletion queue
                print("Already downloaded skipped")
            else:
                print("Downloading")
                try:
                    # code used to download the song and store it in the right folder with the correct file name
                    y.streams.filter(file_extension='mp4').filter(
                        only_audio=True).first().download(output_path=configInfo[x], filename=name)
                    skip = False
                except:
                    # used for a failure in a download to delete the file also and report it to the user.
                    print("ERROR while downloading skipping")
                    try:
                        os.remove(name)
                    except:
                        1
            if not skip: # if the cache for the video needs to be updated it is updated here
                try:
                    # makes the file have the correct metadata
                    file = MP4(name)                         
                    file['©nam'] = videoTitle
                    file['©ART'] = videoAuthor
                    file['©alb'] = videoAlbum
                    file.pprint()
                    file.save()
                    os.rename(name ,configInfo[x] + videoTitle + ".mp3")
                except:
                    print("ERROR metadata could not be saved")
                cacheInfo[y.watch_url] = {"Song": videoTitle, "Artist": videoAuthor, "Album": videoAlbum}
                writeFile(cacheLocation, cacheInfo)
        # goes through every video still left in the deletion queue
        songLen = len(songList)
        howFarVideo = 0
        for y in songList:
            howFarVideo += 1
            os.remove(y)
            print(
                f"Playlist {number} of {configLen}; Deleting video {howFarVideo} of {songLen} located at {y}")
        number += 1
    # updates the cache
    writeFile(cacheLocation, cacheInfo)
    return configInfo


def clearCache(configInfo):  # Clears the cache
    global cacheLocation
    print("Deleting cache")
    try:
        os.remove(cacheLocation)
    except:
        print("Cache not found")
    return configInfo


def show(configInfo):  # print all playlists
    print("List of all playlists")
    howMany = 0
    for x in configInfo:
        howMany += 1
        try:
            playlist = Playlist(x).title
        except:
            playlist = "invalid link"
        print(f"{howMany}. Link: {x}")
        print(f"{howMany}. Name: {playlist}")
        print(f"{howMany}. Storage: {configInfo[x]}")
        print("")
    input("Press enter to continue")
    return configInfo


def edit(configInfo):  # edit one of them
    choice = input("Enter the howmanyth entry you want to change: ")
    try:
        choice = int(choice)
    except:
        choice = 0
    if choice > 0 and choice <= len(configInfo):
        for x in configInfo:
            choice -= 1
            if choice < 1:
                break
        try:
            playlist = Playlist(x).title
        except:
            playlist = "invalid link"
        print(f"Link: {x}")
        print(f"Name: {playlist}")
        print(f"Storage: {configInfo[x]}")
        if input("Enter y to confirm this entry: ") == "y":
            print("If you enter nothing for the following the entry will not change")
            url = input("Enter the url of the playlist: ")
            if url == "":
                url = x
            location = input(
                "Enter the storage location of the playlist; complete path with the / or \\ at the end: ")
            if location == "":
                location = configInfo[x]
            configInfo.pop(x)
            configInfo[url] = location
    else:
        input("Invalid input press enter to continue")
    return configInfo


def delete(configInfo):
    choice = input("Enter the howmanyth entry you want to delete: ")
    try:
        choice = int(choice)
    except:
        choice = 0
    if choice > 0 and choice <= len(configInfo):
        for x in configInfo:
            choice -= 1
            if choice < 1:
                break
        try:
            playlist = Playlist(x).title
        except:
            playlist = "invalid link"
        print(f"Link: {x}")
        print(f"Name: {playlist}")
        print(f"Storage: {configInfo[x]}")
        if input("Enter y to confirm deletion: ") == "y":
            configInfo.pop(x)
    else:
        input("Invalid input press enter to continue")
    return configInfo


def add(configInfo):
    url = input("Enter the url of the playlist: ")
    location = input(
        "Enter the storage location of the playlist; complete path with the / or \\ at the end: ")
    configInfo[url] = location
    return configInfo


def leave(configInfo):
    global configLocation
    writeFile(configLocation, configInfo)
    print("Left program succesfully")
    exit()

def playSong(song):
    song.play()

def play(configInfo): # Used to play a playlist
    choice = input("Enter the howmanyth entry you want to play: ")
    try:
        choice = int(choice)
    except:
        choice = 0
    if choice > 0 and choice <= len(configInfo):
        for x in configInfo:
            choice -= 1
            if choice < 1:
                break
        try:
            playlist = Playlist(x).title
        except:
            playlist = "invalid link"
        print(f"Link: {x}")
        print(f"Name: {playlist}")
        print(f"Storage: {configInfo[x]}")
        songs = glob.glob(configInfo[x] + "*.mp3")
        try:
            while True:
                name = random.choice(songs)
                song = vlc.MediaPlayer(name)
                song.play()
                print(f"Playing: {name}")
                time.sleep(1)
                while song.is_playing():
                    time.sleep(1)
        except KeyboardInterrupt:
            song.stop()
    return configInfo

# list of all functions
options = {
    "u": update,
    "p": show,
    "e": edit,
    "d": delete,
    "a": add,
    "c": clearCache,
    "q": leave,
    "r": play
}
for x in sys.argv[2:]: # runs every choice put after the location automatically.
    try:  # Runs the correct function for which one
        test = options[x]
        skip = False
    except KeyError:
        print("Invalid Input")
        skip = True
    if not skip:
        configInfo = options[x](configInfo)
    writeFile(configLocation, configInfo)
while True:
    # Will give the choices to the user
    choice = input("""
--help menu--
The following are the options
u - will update all playlists
p - will print all playlist links and where they are stored
e - edit a playlist entry
d - delete a playlist entry(Will not delete the actual music files)
a - can be used to add another playlist
c - clear cache used when downloading is not working well
r - used to play a playlist and press ctrl-c to stop playing
q - used to quit
""")
    try:  # Runs the correct function for which one
        test = options[choice]
        skip = False
    except KeyError:
        print("Invalid Input")
        skip = True
    if not skip:
        configInfo = options[choice](configInfo)
    writeFile(configLocation, configInfo)
