#!/usr/bin/env python3

# Origin Write Metadata
# author: hypermodified
# This python script loops through a directory opens the associated origin file, gets the meta data from that and writes it to the vorbis tags in the flac files in the directory
# This script writes to Album Artist, Album, Year, Label, Catalog Number for all albums.
# It will write to Artist as well if you specify that the albums are not Various Artists, DJ or Classical albums.
# If the folder it is checking starts with CD it will use the number of the folder to write to disc number.
# Additionally it will check folders that start with CD for cover art and if it is missing will copy it from the album folder.
# This has only been tested to work with flac files.
# It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters.
# It has been tested and works in both Ubuntu Linux and Windows 10.

# Before running this script install the dependencies
# pip install mutagen

# Import dependencies
import os  # Imports functionality that let's you interact with your operating system
import yaml  # Imports yaml
import shutil  # Imports functionality that lets you copy files and directory
import datetime  # Imports functionality that lets you make timestamps
import mutagen  # Imports functionality to get metadata from music files

#  Set your directories here
album_directory = "M:\PROCESS"  # Which directory do you want to start with?
log_directory = "M:\PROCESS-LOGS\Logs"  # Which directory do you want the log in?

# Set whether you are using nested folders or have all albums in one directory here
# If you have all your ablums in one music directory Music/Album_name then set this value to 1
# If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2
# The default is 1
album_depth = 1

# Set whether you are retagging albums that are various artist, dj, or normal
# Setting this to 1 will only set the Album Artist to the artist name which will be Various Artists
# Setting this to 2 will set the Album Artist tag to the DJ name
# Setting this to 3 will set both Album Artist and Artist tag to the artists name
# 1 = VA
# 2 = DJ
# 3 = Normal
# BE CAREFULL you could accidentally overwrite metadata that will be hard to get back if you have it set to 3
# The default is 1
album_type = 3

# Establishes the counters for completed albums and missing origin files
count = 0
total_count = 0
error_message = 0
good_missing = 0
bad_missing = 0
parse_error = 0
origin_old = 0
copy_cover = 0
disc_number_count = 0
missing_cover = 0

# identifies album directory level
path_segments = album_directory.split(os.sep)
segments = len(path_segments)
album_location_check = segments + album_depth


# A function to log events
def log_outcomes(directory, log_name, message, log_list):
    global log_directory

    script_name = "Origin Write Tags Script"
    today = datetime.datetime.now()
    log_name = f"{log_name}.txt"
    album_name = directory.split(os.sep)
    album_name = album_name[-1]
    log_path = os.path.join(log_directory, log_name)
    with open(log_path, "a", encoding="utf-8") as log_name:
        log_name.write(f"--{today:%b, %d %Y} at {today:%H:%M:%S} from the {script_name}.\n")
        log_name.write(f"The album folder {album_name} {message}.\n")
        if log_list != None:
            log_name.write("\n".join(map(str, log_list)))
            log_name.write("\n")
        log_name.write(f"Album location: {directory}\n")
        log_name.write(" \n")
        log_name.close()


# A function that determines if there is an error
def error_exists(error_type):
    global error_message

    if error_type >= 1:
        error_message += 1  # variable will increment if statement is true
        return "Warning"
    else:
        return "Info"


# A function that writes a summary of what the script did at the end of the process
def summary_text():
    global count
    global total_count
    global error_message
    global parse_error
    global bad_missing
    global good_missing
    global origin_old
    global disc_number_count
    global copy_cover
    global missing_cover

    print("")
    print(f"This script wrote tags to {count} tracks from {total_count} albums.")
    if disc_number_count != 0:
        print(f"It added disc numbers to {disc_number_count} sub folders.")
    if copy_cover != 0:
        print(f"It copied cover art to {copy_cover} sub folders.")
    print("This script looks for potential missing files or errors. The following messages outline whether any were found.")

    error_status = error_exists(parse_error)
    print(f"--{error_status}: There were {parse_error} albums skipped due to not being able to open the yaml. Redownload the yaml file.")
    error_status = error_exists(origin_old)
    print(f"--{error_status}: There were {origin_old} origin files that do not have the needed metadata and need to be updated.")
    error_status = error_exists(bad_missing)
    print(f"--{error_status}: There were {bad_missing} folders missing an origin files that should have had them.")
    error_status = error_exists(good_missing)
    print(f"--Info: Some folders didn't have origin files and probably shouldn't have origin files. {good_missing} of these folders were identified.")
    if missing_cover != 0:
        error_status = error_exists(missing_cover)
        print(f"--{error_status}: There were {missing_cover} folders missing cover art that should have had them.")

    if error_message >= 1:
        print("Check the logs to see which folders had errors and what they were and which tracks had metadata written to them.")
    else:
        print("There were no errors.")


# A function to check whether the directory is a an album or a sub-directory and returns an origin file location and album name
def level_check(directory):
    global total_count
    global album_location_check
    global album_directory

    print(f"--Directory: {directory}")
    print(f"--The albums are stored {album_location_check} folders deep.")

    path_segments = directory.split(os.sep)
    folder_name = path_segments[-1]
    directory_location = len(path_segments)

    print(f"--This folder is {directory_location} folders deep.")

    # Checks to see if a folder is an album or subdirectory by looking at how many segments are in a path and returns origin location and album name
    if album_location_check == directory_location and album_depth == 1:
        print("--This is an album.")
        origin_location = os.path.join(directory, "origin.yaml")
        album_name = path_segments[-1]
        total_count += 1  # variable will increment every loop iteration
        return origin_location, album_name, folder_name
    elif album_location_check == directory_location and album_depth == 2:
        print("--This is an album.")
        origin_location = os.path.join(directory, "origin.yaml")
        album_name = os.path.join(path_segments[-2], path_segments[-1])
        total_count += 1  # variable will increment every loop iteration
        return origin_location, album_name, folder_name
    elif album_location_check < directory_location and album_depth == 1:
        print("--This is a sub-directory")
        origin_location = os.path.join(album_directory, path_segments[-2], "origin.yaml")
        album_name = os.path.join(path_segments[-2], path_segments[-1])
        return origin_location, album_name, folder_name
    elif album_location_check < directory_location and album_depth == 2:
        print("--This is a sub-directory")
        origin_location = os.path.join(album_directory, path_segments[-3], path_segments[-2], "origin.yaml")
        album_name = os.path.join(path_segments[-3], path_segments[-2], path_segments[-1])
        return origin_location, album_name, folder_name
    elif album_location_check > directory_location and album_depth == 2:
        print("--This is an artist folder.")
        origin_location = None
        album_name = None
        return origin_location, album_name, folder_name


# Rethink this so it checks all files and if any end in flac go forth
# A function to check whether a directory has flac and should be checked further
def flac_check(directory):

    # Loop through the directory and see if any file is a flac
    for fname in os.listdir(directory):
        if fname.lower().endswith(".flac"):
            print("--There are flac in this directory.")
            return True

    print("--There are no flac in this directory.")
    return False


# A function to check if the origin file is there and to determine whether it is supposed to be there.
def check_file(directory):
    global good_missing
    global bad_missing
    global album_location_check

    # check to see if there is an origin file
    file_exists = os.path.exists("origin.yaml")
    # if origin file exists, load it, copy, and rename
    if file_exists == True:
        return True
    else:
        # split the directory to make sure that it distinguishes between folders that should and shouldn't have origin files
        current_path_segments = directory.split(os.sep)
        current_segments = len(current_path_segments)
        # create different log files depending on whether the origin file is missing somewhere it shouldn't be
        if album_location_check != current_segments:
            # log the missing origin file folders that are likely supposed to be missing
            print("--An origin file is missing from a folder that should not have one.")
            print("--Logged missing origin file.")
            log_name = "good-missing-origin"
            log_message = "origin file is missing from a folder that should not have one.\nSince it shouldn't be there it is probably fine but you can double check"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            good_missing += 1  # variable will increment every loop iteration
            return False
        else:
            # log the missing origin file folders that are not likely supposed to be missing
            print("--An origin file is missing from a folder that should have one.")
            print("--Logged missing origin file.")
            log_name = "bad-missing-origin"
            log_message = "origin file is missing from a folder that should have one"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            bad_missing += 1  # variable will increment every loop iteration
            return False


#  A function that gets the directory and then opens the origin file and extracts the needed variables
def get_metadata(directory, origin_location, album_name):
    global count
    global parse_error
    global origin_old
    global bad_missing

    print(f"--Getting metadata for {album_name}")
    print(f"--From: {origin_location}")

    # check to see if there is an origin file is supposed to be in this specific directory
    file_exists = check_file(directory)
    # check to see the origin file location variable exists
    location_exists = os.path.exists(origin_location)

    if location_exists == True:
        print("--The origin file location is valid.")
        # open the yaml
        try:
            with open(origin_location, encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print("--There was an issue parsing the yaml file and the cover could not be downloaded.")
            print("--Logged missing cover due to parse error. Redownload origin file.")
            log_name = "parse-error"
            log_message = "had an error parsing the yaml and the cover art could not be downloaded. Redownload the origin file"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            parse_error += 1  # variable will increment every loop iteration
            return
        # check to see if the origin file has the corect metadata
        if "Cover" in data.keys():
            print("--You are using the correct version of gazelle-origin.")

            # turn the data into variables
            origin_metadata = {
                "artist_name": data["Artist"],
                "album_name": data["Name"],
                "release_type": data["Release type"],
                "edition": data["Edition"],
                "edition_label": data["Record label"],
                "edition_cat": data["Catalog number"],
                "edition_year": data["Edition year"],
                "djs": data["DJs"],
                "composers": data["Composers"],
                "conductors": data["Conductors"],
                "original_year": data["Original year"],
                "media": data["Media"],
                "dl_directory": data["Directory"],
            }
            f.close()
            return origin_metadata
        else:
            print("--You need to update your origin files with more metadata.")
            print("--Switch to the gazelle-origin fork here: https://github.com/spinfast319/gazelle-origin")
            print("--Then run: https://github.com/spinfast319/Update-Gazelle-Origin-Files")
            print("--Then try this script again.")
            print("--Logged out of date origin file.")
            log_name = "out-of-date-origin"
            log_message = "origin file out of date"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            origin_old += 1  # variable will increment every loop iteration
    else:
        # log the missing origin file folders that are not likely supposed to be missing
        print("--An origin file is missing from a folder that should have one.")
        print("--Logged missing origin file.")
        log_name = "bad-missing-origin"
        log_message = "origin file is missing from a folder that should have one"
        log_list = None
        log_outcomes(directory, log_name, log_message, log_list)
        bad_missing += 1  # variable will increment every loop iteration


def write_tags(directory, origin_metadata, album_name):
    global count
    global album_type

    print("--Retagging files.")
    # Clear the list so the log captures just this albums tracks
    retag_list = []

    if origin_metadata != None:
        # Loop through the directory and rename flac files
        for fname in os.listdir(directory):
            if fname.endswith(".flac"):
                tag_metadata = mutagen.File(fname)
                print(f"--Track Name: {fname}")
                # log track that was retagged
                retag_list.append(f"--Track Name: {fname}")
                #  retag the metadata
                if origin_metadata["artist_name"] != None and album_type == 1:
                    tag_metadata["ALBUM ARTIST"] = origin_metadata["artist_name"]
                    tag_metadata["ALBUMARTIST"] = origin_metadata["artist_name"]
                if origin_metadata["djs"] != None and album_type == 2:
                    tag_metadata["ALBUM ARTIST"] = origin_metadata["djs"]
                    tag_metadata["ALBUMARTIST"] = origin_metadata["djs"]
                if origin_metadata["artist_name"] != None and album_type == 3:
                    tag_metadata["ALBUM ARTIST"] = origin_metadata["artist_name"]
                    tag_metadata["ALBUMARTIST"] = origin_metadata["artist_name"]
                    tag_metadata["ARTIST"] = origin_metadata["artist_name"]
                if origin_metadata["album_name"] != None:
                    tag_metadata["ALBUM"] = origin_metadata["album_name"]
                if origin_metadata["release_type"] != None:
                    tag_metadata["GROUPING"] = origin_metadata["release_type"]
                    tag_metadata["RELEASETYPE"] = origin_metadata["release_type"]
                if origin_metadata["edition_label"] != None:
                    tag_metadata["ORGANIZATION"] = origin_metadata["edition_label"]
                    tag_metadata["LABEL"] = origin_metadata["edition_label"]
                if origin_metadata["edition_cat"] != None:
                    tag_metadata["LABELNO"] = origin_metadata["edition_cat"]
                    tag_metadata["CATALOGNUMBER"] = origin_metadata["edition_cat"]
                if origin_metadata["media"] != None:
                    tag_metadata["MEDIA"] = str(origin_metadata["media"])
                if origin_metadata["original_year"] != None:
                    tag_metadata["ORIGINALDATE"] = str(origin_metadata["original_year"])
                    tag_metadata["ORIGINALYEAR"] = str(origin_metadata["original_year"])
                    tag_metadata["YEAR"] = str(origin_metadata["original_year"])
                if origin_metadata["edition_year"] != None:
                    tag_metadata["DATE"] = str(origin_metadata["edition_year"])
                elif origin_metadata["edition_year"] == None and origin_metadata["original_year"] != None:
                    tag_metadata["DATE"] = str(origin_metadata["original_year"])
                tag_metadata.save()
                count += 1  # variable will increment every loop iteration
    else:
        print(f"Origin metadata unexpectedly missing.")

    # figure out how many tracks were renamed
    tracks_retagged = len(retag_list)
    if tracks_retagged != 0:
        print(f"--Tracks Retagged: {tracks_retagged}")
    else:
        print(f"--There were no flac in this folder.")
    # log the files that were retagged with metadata
    log_name = "files_retagged"
    log_message = f"had {tracks_retagged} files retagged"
    log_list = retag_list
    log_outcomes(directory, log_name, log_message, log_list)


#  This function adds the disc number tag based off of the number of the folder for multidisc albums using the format CD1, CD2, etc
def add_disc_number(directory, folder_name, album_name):
    global disc_number_count

    print("Adding Disc Number")

    # Clear the list so the log captures just this albums tracks
    adddisc_list = []

    path_segments = folder_name.split()
    disc = path_segments[0]
    disc_number = disc[2:]
    print(f"--The disc number is: {disc_number}")
    if disc_number != None:
        for fname in os.listdir(directory):
            if fname.endswith(".flac"):
                tag_metadata = mutagen.File(fname)
                print(f"--Track Name: {fname}")
                # log track that was retagged
                adddisc_list.append(f"--Track Name: {fname}")
                tag_metadata["DISCNUMBER"] = disc_number
                tag_metadata.save()

    # figure out how many tracks were given disc numbers
    tracks_retagged = len(adddisc_list)
    if tracks_retagged != 0:
        print(f"--Tracks Retagged: {tracks_retagged}")
        disc_number_count += 1  # variable will increment every loop iteration
    else:
        print(f"--There were no flac in this folder.")
    # log the files that were retagged with disc numbers
    log_name = "files_retagged"
    log_message = f"had {tracks_retagged} files retagged with disc number"
    log_list = adddisc_list
    log_outcomes(directory, log_name, log_message, log_list)


# Finds the path of an image with the name 'cover' and an extension of .jpg, .jpeg, .gif, or .png in the given directory.
def check_cover(directory):

    # Check if directory exists
    if not os.path.isdir(directory):
        return None

    # Look for files with the name 'cover' and an appropriate extension
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        if name.lower() == "cover" and ext.lower() in (".jpg", ".jpeg", ".gif", ".png"):
            return os.path.join(directory, filename)

    # If no appropriate file is found, return None
    return None


#  This function adds the disc number tag based off of the number of the folder for multidisc albums using the format CD1, CD2, etc
#  This function prioritises cover.jpg over any other cover files in the folders
def copy_cover_art(directory, album_name):
    global copy_cover
    global missing_cover

    # Check to see if cover art exists in the sub directory
    sub_folder_cover = check_cover(directory)

    # If no cover is present copy the cover art from the folder above to the folder
    if sub_folder_cover == None:
        print("--This subfolder is missing a cover.")

        # Get the path of the source cover art file in the album folder.
        directory_above = os.path.dirname(directory)
        # Try cover.jpg first, if it doesn't exist get the cover art path
        guess_cover = os.path.join(directory_above, "cover.jpg")
        if os.path.exists(guess_cover):
            source_cover_path = guess_cover
        else:
            source_cover_path = check_cover(directory_above)

        # If cover art exists in the album folder copy it to the subfolder
        if source_cover_path:
            #  Build destination directory
            name, ext = os.path.splitext(source_cover_path)
            if ext.lower() == ".jpeg":
                ext = ".jpg"
            destination_cover_art = directory + os.sep + "cover" + ext.lower()

            # Copy cover art
            print("--Copying album cover art to subfolder.")
            shutil.copy(source_cover_path, destination_cover_art)
            print(f"----Source: {source_cover_path}")
            print(f"----Destination: {destination_cover_art}")
            copy_cover += 1  # variable will increment every loop iteration
            # log the sub folders that had cover art copied to them
            log_name = "files_retagged"
            log_message = f"had cover art copied to it"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
        else:
            print("--The cover art is missing from the album folder.")
            missing_cover += 1  # variable will increment every loop iteration
            # log missing cover art
            log_name = "missing_cover_art"
            log_message = f"was missing cover art"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
    else:
        print("--There is a cover in this subfolder.")


# The main function that controls the flow of the script
def main():

    try:
        # intro text
        print("")
        print("I will shred this universe down to its last atom and then, with the stones you've collected for me, create a new one...")
        print("")

        # Get all the subdirectories of album_directory recursively and store them in a list:
        directories = [os.path.abspath(x[0]) for x in os.walk(album_directory)]
        directories.remove(os.path.abspath(album_directory))  # If you don't want your main directory included

        #  Run a loop that goes into each directory identified in the list and runs the function that sorts the folders
        for i in directories:
            os.chdir(i)  # Change working Directory
            print("")
            print("Retagging starting.")
            # establish directory level
            origin_location, album_name, folder_name = level_check(i)
            # check for flac
            is_flac = flac_check(i)
            # check for meta data and sort
            if is_flac == True:
                origin_metadata = get_metadata(i, origin_location, album_name)  # get metadata
                write_tags(i, origin_metadata, album_name)  # write metadata to flac
                if folder_name.startswith("CD"):
                    add_disc_number(i, folder_name, album_name)  # write disc number to flac
                    copy_cover_art(i, album_name)  # copy cover art to CD folders if missing
                print("Retagging complete.")
            else:
                print("No retagging.")

    finally:
        # Summary text
        print("")
        print("...It is not what is lost but only what it is been given... a grateful universal.")
        # run summary text function to provide error messages
        summary_text()
        print("")


if __name__ == "__main__":
    main()
