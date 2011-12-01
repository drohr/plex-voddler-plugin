# voddler plex plugin 

* Orignal code and idea by Thomas Rosenqvist <thomas@rosenqvist.org>
* Rewriten and maintained by David Röhr <david@rohr.se>
* Images by Sara Smedman <sara@joforik.net>

Very exprimental state, some features work, some dont't. Tested on MacOSX and Windows with PMS 0.9.5.x

## Features

* Playback on AVOD "Play" movies, documentaries and series
* Playback of trailers
* Browsing all types of movies, documentaries and series
* Searching for content
* Browsing Favorites, Playlist and History
* Sorting settings in preferences
* Adult filter setting in preferences
* Thumbnails and movie/episode information where available
* Plex Plugin installer package for MacOSX users for easy install

## Known Issues

* No playback on rental movies, only browsing.
* When changing a setting you could sometimes get an error msg.
* You can't choose to resume a movie or not, if a resume point exists, then it will resume
* Sometimes Plex tries to transcode movies even though it doesn't need to.
* Seekbar not working, should be fixed with javascript support
* Not listed in plex store

## ChangeLog

* 2.7
    * Major code clean up
    * Added documentation
    * Added AdultFilter
    * Added Trailers
* 2.2
    * Support added for browsing playlist, favorites and history
* 2.0
    * Support added for series
* 1.0
    * Added new look and feel
    * More rewrites
* 0.5
    * Major code writes
    * Support for resume points
    * Initial support for series
* 0.1
    * Initial release
