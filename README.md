# Origin-Write-Tags
### A python script that loops through a directory, opens the associated origin file, gets the metadata from that and writes it to the vorbis tags for all flac files in the directory. This script writes to Album Artist, Album, Year, Label, Catalog Number for all albums.

It will write to Artist as well if you specify that the albums are not Various Artists, DJ or Classical albums.

This project has a dependency on the gazelle-origin project created by x1ppy. gazelle-origin scrapes gazelle based sites and stores the related music metadata in a yaml file in the music albums folder. For this script to work you need to use a fork that has additional metadata including the cover art. The fork that has the most additional metadata right now is: https://github.com/spinfast319/gazelle-origin

This has only been tested to work with flac files and would need to be modified to work with mp3 or other types of music files. The script can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters. It has been tested and works in both Ubuntu Linux and Windows 10.

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


