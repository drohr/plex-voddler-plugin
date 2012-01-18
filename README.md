# Plex Plugin for the Voddler movie service 

Voddler is an online film service, that offer movies, TV-series and documentaries for you to watch online, legally, streamed directly to your computer screen or TV-set. <http://www.voddler.com>

The Plugin has been tested and developed on MacOSX (PMS 0.9.5.x) but should work well on Windows Vista or Windows 7.

![plex-voddler-plugin](https://github.com/drohr/plex-voddler-plugin/raw/master/browse.jpg)

## Credits

* Orignal idea by Thomas Rosenqvist 
* Icons by Sara Smedman

## Manual Installation
Downloads: <https://github.com/drohr/plex-voddler-plugin/downloads>

Make sure you have the latest Plex Media Server with the proper flash plugin installed. Most movies also require you to use the VoddlerNet application.

* For Mac (Plexapp)
    * Download the voddler.plexapp zip
    * Extract and Click for install
* For Mac (Bundle)
    * Download the voddler.bundle zip 
    * Move/Extract it to ~Library/Application Support/Plex Media Server/Plug-ins
* For Windows (Bundle)
    * Download the voddler.bundle zip 
    * Right-click the Plex Media Server icon in the Windows System Tray and choose Open Plug-ins Folder
    * Copy the extracted voddler.bundle to that folder 

## Features

* Playback
    * Playback on "Play" and Rental movies, documentaries and series
    * Playback of trailers
    * Working seekbar, with proper play/pause functionality
    * Subtitles when enabled and available
* Browsing
    * Browsing all types of movies, documentaries and series
    * Searching for content
    * Browsing Favorites, Playlist and History
    * Option to Add/Remove movies to playlists
    * Thumbnails and movie/episode meta data where available
* Payments
    * Payment options of premium vouchers or ticket codes
* Preferences
    * List settings (Play/Rental/All) 
    * Sorting settings (Alphabetical/Added/Rating/Views) 
    * Option to enable Adult content 
    * Option to set amount of Search Results
    * Option to set subtitle language and size

## Known Issues

* You can't choose to resume a movie or not, if a resume point exists, then the player will ignore it and start from the beginning (TODO)
* If you seek in the movie, the duration time is not updated correctly
* The search disregardes the adultfilter and doesn't allow adult content (server side mabye?)
* Transcoded video is not fully supported and has some glitches

## ChangeLog

* 2.2
    * Rental movies are now playable
    * Standard seekbar replaced with javascript and is now working
* 2.1
    * You can now choose subtitle language and size in settings
* 2.0
    * You can now rent movies using premium vouchers or ticket codes
    * Added Search results option
    * Enhanced browsing speed
    * Added add/remove from Favorites or Playlist
    * Added Documentation
    * Added AdultFilter
    * Added Trailers
    * Added Playlist, Favorites and History
    * Added Series
* 1.0
    * Added new look and feel
    * Playback on "Play" movies
    * Support for resume points
    * Initial support for multiple languages
    * Initial support for Movies & Series
* 0.1
    * Initial release
