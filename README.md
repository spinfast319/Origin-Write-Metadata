# Origin-Write-Metadata
### A python script that loops through a directory, opens the associated origin file, gets the metadata from that, and writes it to the vorbis tags for all flac files in the directory. This script writes to Album Artist, Album, Year, Label, Catalog Number for all albums.

If you source your music from a site that has good metadata and you can access and store that data in a origin file, you may want to write that metadata directly to the flac files to standardize the tags for the albums.  Reasons you may want to do this are that while public sources such as the api's for discogs, musicbrainz, beatport etc might have good metadata, they might not have metadata for all of the music in your collection and the metadata they have might not match the exact release you have. 

This script will loop through your music directory and open each origin file that it finds. It then extracts the relevent metadata and writes it to the vorbis comments for all the flac files in the album. The source data of the origin files does not have individual track information, it only has album information. The mapping it does from the origin file data model to the flac vorbis comments model is:
- The origin files _Name:_ field gets written to the vorbis _ALBUM_ field. (ie. the albums name)
- The origin files _Release type:_ field gets written to the vorbis _GROUPING_ and _RELEASETYPE_ fields. (ie. album, ep, etc)
- The origin files _Record label:_ field gets written to the vorbis _ORGANIZATION_ and _LABEL_ fields. 
- The origin files _Catalog number:_ field gets written to the vorbis _LABELNO_ and _CATALOGNUMBER_ fields.
- The origin files _Media:_ field gets written to the vorbis _MEDIA_ field. (ie. cd, web, vinyl, etc)
- The origin files _Original year:_ field gets written to the vorbis _ORIGINALDATE_, _ORIGINALYEAR_, and _YEAR_ fields.
- The origin files _Edition year:_ field gets written to the vorbis _DATE_ field.

The script will also use the _Artist_ field as well but will do different things if you specify that the albums are Various Artists, DJ or Classical albums. 

For normal albums the script maps:   
- The origin files _Artist:_ field gets written to the vorbis _ALBUM ARTIST_ and _ARTIST_ fields. 
 
For compliations the script maps:   
- The origin files _Artist:_ field gets written to the vorbis _ALBUM ARTIST_ field only. It leaves the ARTIST field as is.   

For DJ mixes the script maps:   
- The origin files _DJs:_ field gets written to the vorbis _ALBUM ARTIST_ field only. It leaves the ARTIST field as is.

It doesn't yet have functionality to work for classical albums with composers and conductors but this will like be added in the future.

Additionally, the script can write to the vorbis _DISCNUMBER_ field.  It is designed to be run after the [Standard-Folder](https://github.com/spinfast319/Standard-Folder) script which will name all sub-directories with flac in them to the format of _CD1_, _CD2_, etc. If this script encounters sub-directories with that naming structure it will write the number that follows the letters CD to the vorbis _DISCNUMBER_ field.  After it does that, it checks to see if the sub-directory has a cover art image in it.  If the cover art is missing, it copies the cover art from the album directory to the sub-directory. It logs all the retagging and copying it does and will also log missing cover art.

This script does not write the _Tags_ to the _GENRE_ field. There is a seperate set of scripts that deal with genres and styles. [Origin-Combine-Genres](https://github.com/spinfast319/Origin-Combine-Genres) merges the _GENRE_, _MOOD_ and _STYLE_ comments from the flac with the _Tags_ field and [Origin-Write-Genres](https://github.com/spinfast319/Origin-Write-Genres) determines which ones should be genres and which ones should be styles and writes them to the correct vorbis comments.

Once the metadata from the origin files is properly written to the flac files you will likely need to configure your music player to see and use non normative metadata.  Full featured music application like MusicBee and Foobar2000 will be able to do this.

This script has only been tested to work with flac files and would need to be modified to work with mp3 or other types of music files. The script can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters. It has been tested and works in both Ubuntu Linux and Windows 10.

This script is meant to work in conjunction with other scripts in order to manage a large music library when the source of the music has good metadata you want to use to organize it.  You can find an overview of the scripts and workflow at [Origin-Music-Management](https://github.com/spinfast319/Origin-Music-Management). 

## Dependencies
This project has a dependency on the gazelle-origin project created by x1ppy. gazelle-origin scrapes gazelle based sites and stores the related music metadata in a yaml file in the music albums folder. For this script to work you need to use a fork that has additional metadata including the tags and coverart. The fork that has the most additional metadata right now is: https://github.com/spinfast319/gazelle-origin

All your albums will need origin files origin files associated with them already for this script to work.

It also has a dependency on the python project Mutagen, which is a library for manipulating music metadata. Instructions on installing it are below.

## Install and set up
1) Clone this script where you want to run it.

2) Install [mutagen](https://pypi.org/project/mutagen/) with pip. (_note: on some systems it might be pip3_) 

to install it:

```
pip install mutagen
```

3) Edit the script where it says _Set your directories here_ to set up or specify two directories you will be using. Write them as absolute paths for:

    A. The directory where the albums you want to write metadata to are stored  
    B. The directory to store the log files the script creates  

4) Edit the script where it says _Set whether you are using nested folders_ to specify whether you are using nested folders or have all albums in one directory 

    A. If you have all your ablums in one music directory, ie. Music/Album then set this value to 1 (the default)  
    B. If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2  

5) Edit the script where it says _Set whether you are retagging albums that are various artist, dj, or normal_ to specify whether you want to write data to the artist field and if so what data. ***BE CAREFULL*** you could accidentally overwrite metadata that will be hard to get back if you have it set to 3 as it could write _"Various Artists"_ over all the artist fields.  This is because origin files have metadata for albums not tracks.

    - If you are tagging compilations with many different artists on them set this value to 1 (the default)
      - This will write _"Various Artists"_ to the album artist field and leave all track artist fields unchanged   
      - This default since it is the least risky choice.   
    - If you are tagging mixes which have a dj or complier and have tracks with many different artists on them set this value to 2
      - This will write the DJ or compiler's name to the album artist field and leave all track artist fields unchanged     
    - If you are tagging normal albums where the same artist wrote all the tracks set this value to 3
      - This will write the album artist name to the album artist field and the artist field for each track
      - This is the most common situation but will write over anything that is already there. 

6) Use your terminal to navigate to the directory the script is in and run the script from the command line.  When it finishes it will output how many albums have had metadata written to them.

```
Origin-Write-Metadata.py
```

_note: on linux and mac you will likely need to type "python3 Origin-Write-Metadata.py"_  
_note 2: you can run the script from anywhere if you provide the full path to it_

The script will also create logs listing any album that it has problems processing.  


