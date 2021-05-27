#! /usr/bin/env python3
from pytube import YouTube, Playlist
import sys
import os
import json
import glob
print("youtubeMusic downloader is starting! This program can be used to download your music playlist from youtube for free in a fast and easy way!")


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


def update(configInfo):  # updates all playlists
    number = 1
    configLen = len(configInfo)
    for x in configInfo:
        try:
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
        howFarVideo = 0
        videoLen = len(playlist.videos)
        songList = glob.glob(configInfo[x] + "/*.mp4")
        for y in playlist.videos:
            howFarVideo += 1
            print(
                f"Playlist {number} of {configLen}; Video {howFarVideo} of {videoLen} called {y.title}; ", end= '')
            name = y.streams.filter(only_audio=True).first().download(
                output_path=configInfo[x])
            try:
                songList.remove(name)
                print("Already downloaded skipped")
            except:
                print("Downloading")
        songLen = len(songList)
        howFarVideo = 0
        for y in songList:
            howFarVideo += 1
            os.remove(y)
            print(f"Playlist {number} of {configLen}; Deleting video {howFarVideo} of {songLen} located at {y}")
        number += 1
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
        playlist = Playlist(x).title
        print(f"Link: {x}")
        print(f"Name: {playlist}")
        print(f"Storage: {configInfo[x]}")
        if input("Enter y to confirm this entry: ") == "y":
            print("If you enter nothing for the following the entry will not change")
            url = input("Enter the url of the playlist: ")
            if url == "":
                url = x
            location = input(
                "Enter the storage location of the playlist; complete path: ")
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
        "Enter the storage location of the playlist; complete path: ")
    configInfo[url] = location
    return configInfo


def leave(configInfo):
    global configLocation
    writeFile(configLocation, configInfo)
    print("Left program succesfully")
    exit()


print("Searching for configuration files")
try:  # Will check for the arguement for the location of the config
    location = sys.argv[1]
    if location[-1] == "/":
        location = location[:-1]
    configLocation = location + "/.config.json"
except:
    print("argument missing for working directory using directory of program")
    location = str(os.getcwdb())[2:-1]
    configLocation = location + "/.config.json"
if not os.path.isdir(location):  # Will check if the folder for the config exists
    os.makedirs(location)
    print("Folder did not exist created new folder at" + location)
# Will find the config file and create a new one if it does not exist
if not os.path.isfile(location + "/.config.json"):
    print("New folder detected creating new config")
    writeFile(configLocation, {})
    configInfo = {}
else:
    configInfo = readFile(configLocation)
    print("Found Configuration files")
# list of all functions
options = {
    "u": update,
    "p": show,
    "e": edit,
    "d": delete,
    "a": add,
    "q": leave
}
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
q - used to quit
""")
    try:  # Runs the correct function for which one
        test = options[choice]
        skip = False
    except:
        print("Invalid Input")
        skip = True
    if not skip:
        configInfo = options[choice](configInfo)
    writeFile(configLocation, configInfo)