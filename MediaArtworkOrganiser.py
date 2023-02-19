# Program to move downloaded artwork to corresponding movie folder in the plex database, and to rename them accordingly.

# Imports the necessary modules. These should all be standard with Python 3. However, you can download them via PIP if necesary. 
import os
import shutil
import glob
import re
import sys

import difflib
from difflib import SequenceMatcher

import pathlib
from pathlib import Path

# Clears any previous console output to make the program more readable.
os.system("cls")


# This can either be 'poster' or 'fanart', poster is the movie cover seen on the plex library screen, and 'fanart' is the
# background of the movie play screen.

# [e.g. "poster"]
artworkType = "poster"


def directoryCheck(directory):

    dir = Path(directory)

    dir_parts = dir.parts
    part_index = 1

    rel_path = dir_parts[0]

    if os.path.exists(dir):
        return dir
    
    else:
        while (part_index < len(dir_parts)):

            minimum_match_ratio = 0.7
            best_match = ""
            rel_path_contents = os.listdir(rel_path)

            for file in rel_path_contents:
                ratio = SequenceMatcher(None, file, dir_parts[part_index]).ratio()

                if ratio > minimum_match_ratio:
                    minimum_match_ratio = ratio
                    best_match = file

            if best_match != "":
                rel_path = rel_path + "\\" + best_match
                part_index += 1

            else:
                rel_path = None
                break
            
    return rel_path

        
def userInputBool(default="yes"):

    valid_input = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    
    while True:
        sys.stdout.write(prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid_input[default]
        elif choice in valid_input:
            return valid_input[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def directoryInput(type="artwork"):

    validInput = False

    while validInput == False:

        if type == "artwork":
            print('[e.g. "C:/Pictures/downloaded_art"]')

        elif type == "media":
            print('[e.g. "P:/Videos/Plex/Movies"]')
            print('[e.g. "//<server_ip>/Plex/Movies"]')

        dir = ((pathlib.PureWindowsPath(input("Enter the {} directory: ".format(type)))).as_posix()).strip("\"")

        if os.path.exists(dir):
            break

        else:
            corrected_dir = directoryCheck(dir)
            if not corrected_dir:
                print("Cannot find the art directory. Please try again.")

            else:
                print("Did you mean {}?".format(corrected_dir))
                choice = userInputBool("yes")
                print("\n")

                if choice:
                    dir = ((pathlib.PureWindowsPath(corrected_dir)).as_posix()).strip("\"")
                    validInput = True
                
                else:
                    print("Please enter a valid directory\n")
                    continue

    return dir



# Directory of the artwork that is to be moved to the movie folders. The '**' means any subdirectory after that point. Make 
# the directory as specific as possible to avoid indexing a large amount of unnecessary files. The movie artwork must have 
# the same name as the movie and the correct data in brackets [e.g. Casino Royale (2006)], however it is case insensitive,
# and ignores all grammar (except brackets), so misplaced dashes, commas etc. will still result in a correct match.
# Directory must be surrounded in apostrophes ["<directory>"]. Make sure to use forward slashes, not back slashes!

# [e.g. "C:/Pictures/downloaded_art/**/"]
artDir = directoryInput(type="artwork")

# Directory of the movies you want to apply artwork to. The '**' means any subdirectory after that point. Make the directory
# as specific as possible to avoid errors and to speed up the process.
# Directory must be surrounded in apostrophes ["<directory>"]. Make sure to use forward slashes, not back slashes!

# [e.g. "P:/Videos/Plex/Movies/**/"]
# [e.g. "//<server_ip>/Plex/Movies/**/"]
dstDir = directoryInput(type="media")

os.system("cls")

print("Artwork Directory: ", artDir)
print("Media Directroy: ", dstDir)

artDir += "/**/"
dstDir += "/**/"


# Used to make the console output look a bit more user-friendly.
termSize = int(os.get_terminal_size()[0])
def seperator():
    print("-"*termSize)


# Compares source and destination directories for matching films, and checks if artwork already exists. If it doesn't, it
# renames and moves the artwork in accordance to plex local media asset guidelines.
def matchFolder(src, dst, artType):
    # Plex supported image formats
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.tbn")
    # Initiate lists of all supported artwork and movie folder paths
    matchingArtwork = []
    matchingMovies = []
    # Initate lists of formatted artwork file and movie folder names mapped to their paths
    mappedArtwork = []
    mappedMovies = []
    # Appends all supported artwork paths to a list
    for ext in extensions:
        matchingArtwork.extend(glob.glob(os.path.join(src, ext), recursive = True))
    # Maps the artwork paths to their formatted names, so slight differences in names (such as dashes),
    # will still match with plex movie folders
    for srcFile in matchingArtwork:
        formSrc = re.sub("[-':;., ]", "", os.path.splitext(os.path.basename(os.path.normpath(srcFile)))[0])
        srcDict = {}
        srcDict[formSrc] = srcFile
        mappedArtwork.append(srcDict)
    # Appends all movie folder paths to a list
    matchingMovies.extend(glob.glob(dst, recursive = True))
    # Maps the movie folder paths to their formatted names, so they can be matched to the artwork despite
    # slight differences in the name
    for dstFile in matchingMovies:
        formDst = re.sub("[-':;., ]", "", os.path.basename(os.path.normpath(dstFile)))
        dstDict = {}
        dstDict[formDst] = dstFile
        mappedMovies.append(dstDict)
    seperator()
    print("SEARCHING")
    seperator()
    # Number of movie folders without artwork that are available in the art directory
    matchNum = 0
    # Loop through the list of mapped artwork and the list of mapped movie folders
    for art in mappedArtwork:
            for movie in mappedMovies:
                # Loop through the keys of the list items to check for matches
                for key in art:
                    # If a corresponding movie folder and artwork are found, continue
                    if key in movie:
                        # Checks to see if a movie poster already exists, if so; skip
                        if glob.glob(os.path.join(movie[key], artType + ".*")):
                            continue
                        # If there is no exisiting movie poster, and one is available; copy it from the source 
                        # directory to the corresponding move folder and provide a console output
                        else:
                            shutil.copy(art[key], os.path.join(movie[key], artType + os.path.splitext(art[key])[1]))
                            matchNum = matchNum + 1
                            print("├◄◄ {}".format((art[key]).replace("\\", "/")))
                            print("│")
                            print("└►► {}".format((os.path.join(movie[key], artType + os.path.splitext(art[key])[1])).replace("\\", "/")))
                            seperator()
    # Displays the number of matches (the number of posters that have been moved)
    if matchNum == 0:
        print("NO NEW", artType.upper() + "S")
    else:
        print(matchNum,"NEW",artType.upper() + "(S)")
    seperator()


# Calls the matchFolder function above, and specifies the paramaters. The source directory, the destination directory, and
# the type of artwork being organised.
matchFolder(artDir, dstDir, artworkType)
