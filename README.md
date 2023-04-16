# Origin-Write-Tags
### A python script that loops through a directory, opens the associated origin file, gets the metadata from that and writes it to the vorbis tags for all flac files in the directory. This script writes to Album Artist, Album, Year, Label, Catalog Number for all albums.

It will write to Artist as well if you specify that the albums are not Various Artists, DJ or Classical albums.
This has only been tested to work with flac files.
It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters.
It has been tested and works in both Ubuntu Linux and Windows 10.
