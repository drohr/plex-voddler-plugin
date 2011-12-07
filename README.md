# Plex Plugin for the Voddler movie service 

* Maintained and developed by David Röhr <david@rohr.se>
* Orignal idea and code by Thomas Rosenqvist <thomas@rosenqvist.org>
* Images by Sara Smedman <sara@joforik.net>

Very beta state, some features work, some dont't. Tested on MacOSX and Windows with PMS 0.9.5.x

## Features

* Playback
    * Playback on "Play" movies, documentaries and series
    * Playback of trailers
* Browsing
    * Browsing all types of movies, documentaries and series
    * Searching for content
    * Browsing Favorites, Playlist and History
    * Thumbnails and movie/episode meta data where available
* Preferences
    * List settings (Play/Rental/All) 
    * Sorting settings (Alphabetical/Added/Rating/Views) 
    * Option to enable Adult content 
    * Option to enable Movie Background Art 

## Known Issues

* No playback on rental movies, only browsing. (server side issue)
* When changing a setting you could sometimes get an error msg.
* You can't choose to resume a movie or not, if a resume point exists, then it will resume
* Browsing for movies show movies for all platforms, not just web
* Sometimes Plex tries to transcode movies even though it doesn't need to. (probably some wierd PMS bug)
* Seekbar not working, should be fixed with javascript support
* The search disregardes the adultfilter and doesn't allow adult content (server side mabye?)

## ChangeLog

* 1.5
    * More clean up
    * POST instead of GET and also reduced the amount of requests
    * Added Movie art option
* 1.4
    * Added add/remove from Favorites or Playlist
* 1.3
    * Major code clean up
    * Added Documentation
    * Added AdultFilter
    * Added Trailers
* 1.2
    * Added Playlist, Favorites and History
* 1.1
    * Added Series
* 1.0
    * Added new look and feel
    * More rewrites
    * Playback on "Play" movies
* 0.5
    * Support for resume points
    * Initial support for more languages then english
    * Initial support for Movies & Series
* 0.1
    * Initial release
