# -*- encoding: utf-8

import re
import time
from urlparse import urlparse

############################################################################################

VERSION        = "2.2.0"
VIDEO_PREFIX   = "/video/voddler"
NAME           = L('Title')
ART            = 'art-default.jpg'
ICON           = 'icon-default.png'

API_META       = 'https://api.voddler.com/metaapi/'
API_USER       = 'https://api.voddler.com/userapi/'
API_PAYMENT    = 'https://api.voddler.com/paymentapi/'
API_PLAY       = 'http://www.voddler.com/playapi/'
API_VNET       = 'http://api.voddler.com/vnet/'

NO_ITEMS       = MessageContainer('No Results','No Results')
TRY_AGAIN      = MessageContainer('Error','An error has happened. Please try again later.')
ERROR          = MessageContainer('Network Error','A Network error has occurred')

############################################################################################

def ValidatePrefs():
    """
    Validates prefrences.
    Checks if username, password and filter options are set

    """

    u = Prefs['username']
    p = Prefs['password']
    f = Prefs['filter'] 

    if u == None or p == None:
        return MessageContainer(
            "Error",
            "You need to provide a username and password to use this service"
        )
    elif f == None:
        return MessageContainer(
            "Error",
            "You must have a valid filter setting"
        )
    else:
        pass


def getFilterOptions():
    """
    Returning filter preferences.
    If no value is set, return "free"

    @rtype: str
    @return: Filter setting
    """

    if Prefs['filter'] == "prefs_catFree":
       filter = "free" 
    elif Prefs['filter'] == "prefs_catPremium":
       filter = "premium"
    elif Prefs['filter'] == "prefs_catAll":
       filter = "all"
    else:
       filter = "free"
    return filter


def getSortOptions():
    """
    Returning sorting preferences
    If no value is set, return "alphabetical"

    @rtype: str
    @return: Sorting order
    """

    if Prefs['sortorder'] == "prefs_sortRating":
       sortorder = "rating" 
    elif Prefs['sortorder'] == "prefs_sortViews":
       sortorder = "views"
    elif Prefs['sortorder'] == "prefs_sortAlphabetical":
       sortorder = "alphabetical"
    elif Prefs['sortorder'] == "prefs_sortAdded":
       sortorder = "added"
    else:
       sortorder = "alphabetical"
    return sortorder 


def getSubtitleLang():
    """
    Returning subtitle language from preferences
    If no value is set, return "Off"

    @rtype: str
    @return: Subtitle choice 
    """

    if Prefs['subtitlelang'] == "prefs_SubtitleSV":
       subLanguage = "sv_SE" 
    elif Prefs['subtitlelang'] == "prefs_SubtitleFI":
       subLanguage = "fi_FI"
    elif Prefs['subtitlelang'] == "prefs_SubtitleNK":
       subLanguage = "no_NO"
    elif Prefs['subtitlelang'] == "prefs_SubtitleDK":
       subLanguage = "da_DK"
    elif Prefs['subtitlelang'] == "prefs_SubtitleNone":
       subLanguage = "Off"
    else:
       subLanguage = "Off"
    return subLanguage


def getSubtitleSize():
    """
    Returning subtitle size from preferences
    If no value is set, return "4"

    @rtype: str
    @return: Subtitle choice 
    """

    if Prefs['subtitlesize'] == "prefs_SubtitleBig":
       subSize = "8" 
    elif Prefs['subtitlesize'] == "prefs_SubtitleMedium":
       subSize = "4"
    elif Prefs['subtitlesize'] == "prefs_SubtitleSmall":
       subSize = "2"
    else:
       subSize = "4"
    return subSize


def validateUser():
    """
    Sends a POST request with the username and password provided, sets the user session if successful

    """

    URL = API_USER + "login/1" 
    try:
        # POST
        g = JSON.ObjectFromURL(URL, values={'username': Prefs['username'],
                                            'password': Prefs['password']}, cacheTime=300)
    except Exception:
        Log.Exception('Failed to log in')
        return MessageContainer("Failed to log in", "Problem with communicating with Voddler\nPlease try again later")
    else:
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']


def getVnetSession():
    """
    Returns vnet session as a Dict

    """
    # GET vnet token
    URL = API_USER + "vnettoken/1"
    try:
        # POST
        g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId']}, cacheTime=5)
    except Exception:
        Log.Exception('Failed to get token')
        return MessageContainer("Failed to get token", "Problem with communicating with Voddler\nPlease try again later")
    else:
        token = g["data"]["token"]
        Log.Info('vnet token: %s' % token)
       
        # GET vnet session with vnet token 
        URL = API_VNET + "index/login-token/"
        try:
            # POST
            j = XML.ObjectFromURL(URL, values={'token': token, 'version': '2'}, cacheTime=5)
        except Exception:
            Log.Exception('Failed to login to vnet')
            return MessageContainer("Failed to login to vnet", "Problem with communicating with Voddler\nPlease try again later")
        else:
            vnet_session = j.session_key
            return vnet_session


def setSubtitle():
    """
    Set subtitles using vnet

    """
    try:
        vnet_session = getVnetSession()
    except Exception:
        Log.Exception('Failed to get vnet session')
        return MessageContainer("Failed to get vnet session", "Problem with communicating with Voddler\nPlease try again later")
    else:
 
        # Set subtitle language and size from plex options 
        subLanguage = getSubtitleLang()
        subSize = getSubtitleSize()
        Log.Info('Setting subtitle to: %s %s' % (subLanguage, subSize))
        URL = API_VNET + "settings/"
        try:
            # POST
            sub = XML.ObjectFromURL(URL, values={'session': vnet_session, 'key.1': 'subtitle', 'value.1': subLanguage, 'key.2': 'subtitleSize', 'value.2': subSize}, cacheTime=5)
        except Exception:
            Log.Exception('Failed to set subtitle')
            return MessageContainer("Failed to set subtitle", "Problem with communicating with Voddler\nPlease try again later")
        else:
            pass


def Start():
    """
    Initialize the plugin.

    """

    Plugin.AddPrefixHandler(VIDEO_PREFIX, ShowTypes, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("MediaPreview", viewMode="MediaPreview", mediaType="items")
    Plugin.AddViewGroup("Showcase", viewMode="Showcase", mediaType="items")
    Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
    Plugin.AddViewGroup("PanelStream", viewMode="PanelStream", mediaType="items")
    Plugin.AddViewGroup("WallStream", viewMode="WallStream", mediaType="items")
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "InfoList"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'
    Log.Info('Voddler Plugin initialized')


def ShowTypes():
    """
    Shows the start menu.

    @rtype: str
    @return: MediaContainer with options
    """
    
    Log.Info('Showing Default Menu options')
    dir = MediaContainer(viewGroup="InfoList")

    # search
    addSearch(dir)
    # list movie genres
    dir.Append(
        Function(
            DirectoryItem(listMovieGenres,
                title = Locale.LocalString('menu_Movies'),
                subtitle="",
                summary="Current releases, classic blockbusters and world cinema",
                thumb=R('plex_icon_movies.png'),
                art=R(ART)
            ), genreCategory = "movies", browseType = "movie"
        )
    )
    # list tv show genres
    dir.Append(
        Function(
            DirectoryItem(listMovieGenres,
                title = Locale.LocalString('menu_TVShows'),
                subtitle="",
                summary="The best series from Hollywood, BBC and many others",
                thumb=R('plex_icon_series.png'),
                art=R(ART)
            ), genreCategory = "episodes", browseType = "series"
        )
    )
    # list movie genres (documentaries)
    dir.Append(
        Function(
            DirectoryItem(listMovieGenres,
                title = Locale.LocalString('menu_Documentaries'),
                subtitle="",
                summary="Learn about history, art, food, geography, science, nature, technology and more",
                thumb=R('plex_icon_docus.png'),
                art=R(ART)
            ), genreCategory = "documentary", browseType = "documentary"
        )
    )
    # list favorites
    dir.Append(
        Function(
            DirectoryItem(listPlaylist,
                title = Locale.LocalString('menu_Favorites'),
                subtitle="",
                summary="List of all your favorite movies",
                thumb=R('plex_icon_favorites.png'),
                art=R(ART)
            ), playlistType = "favorites"
        )
    )
    # list playlist
    dir.Append(
        Function(
            DirectoryItem(listPlaylist,
                title = Locale.LocalString('menu_Playlist'),
                subtitle="",
                summary="List of all movies in your current playlist",
                thumb=R('plex_icon_playlist.png'),
                art=R(ART)
            ), playlistType = "playlist"
        )
    )
    # list history
    dir.Append(
        Function(
            DirectoryItem(listPlaylist,
                title = Locale.LocalString('menu_History'),
                subtitle="",
                summary="List of the 100 latest Voddler movies and episodes you have watched",
                thumb=R('plex_icon_history.png'),
                art=R(ART)
            ), playlistType = "history"
        )
    )

    # preference tab
    dir.Append(
        PrefsItem(
            title = Locale.LocalString('menu_Preferences'),
            subtitle="Set up Voddler access details",
            summary="Make sure the VoddlerNet service is enabled.",
            thumb=R('plex_icon_settings.png'),
            art=R(ART)
        )
    )

    return dir


def listMovieGenres(sender, genreCategory, browseType):
    """
    Creates a MediaContainer with a list of Movie genres based on genreCategory

    @type sender: 
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type genreCategory: str
    @param genreCategory: Sub-category of video (movie, documentary or episodes)

    @type browseType: str
    @param browseType: Type of video (movie, documentary or series)
    
    @rtype: str
    @return: MediaContainer
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()

    if Prefs['username'] != None:
        validateUser()

    Log.Info('Listing genres for: %s' % genreCategory)
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)

    URL = API_META + "genres/1?type=" + genreCategory
    try:
        # GET
        g = JSON.ObjectFromURL(URL, cacheTime=500)
    except Exception:
        Log.Exception('Failed to list genres')
        return MessageContainer("Failed to list genres", "Problem with communicating with Voddler\nPlease try again later")
    else:
        """
        dir.Append Search to the output
        """        
        addSearch(dir)
        """
        set the browse thumb icons
        fetch all genre data
        add or disregard the adult genres
        dir.Append items with the correct browseType 
        """
        if browseType == "movie":
            thumbIcon = R('plex_icon_movies.png')
            genreSub = "Movies"
        elif browseType == "documentary":
            thumbIcon = R('plex_icon_docus.png')
            genreSub = "Documentaries"
        elif browseType == "series":
            thumbIcon = R('plex_icon_series.png')
            genreSub = "TV Shows"
        else:
            thumbIcon = R(ICON) 
            genreSub = ""

        for genre in g['data']:
            # disables adult genres if adultfilter is off
            if Prefs['adultfilter'] == False:
                if genre["value"] == "explicit" or genre["value"] == "gay":
                    continue
            dir.Append(
                Function(
                    DirectoryItem(openMovieGenre,
                        genre['name'],
                        subtitle = genreSub,
                        summary = "",
                        thumb = thumbIcon,
                        art = R(ART)
                    ), genre = genre['value'], browseType=browseType
                )
            )
    return dir


def listPlaylist(sender, playlistType):
    """
    Creates a MediaContainer with a list of Movies, Documentaries or TV Show Episodes based on playlistType

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.
    
    @type playlistType: str
    @param playlistType: Type playlist you want to return
    
    @rtype:
    @return: MediaContainer with options
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()

    if Prefs['username'] != None:
        validateUser()

    Log.Info('Listing Playlist: %s' % playlistType)
    dir = MediaContainer(viewGroup="WallStream", title2=sender.itemTitle)

    URL = API_USER + "playlists/1"
    try:
        # POST
        g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId']}, cacheTime=5)
    except Exception:
        Log.Exception('Failed to list playlist')
        return MessageContainer("Failed to list playlist", "Problem with communicating with Voddler\nPlease try again later")
    else:
        for p in g["data"]["playlists"]:
            if p["type"] == playlistType:
                i = 0
                for v in p["videos"]:
                    i = i + 1
                    # get all information for specific video
                    URLinfo = API_META + "info/1?videoId=" + v['id']
                    # GET
                    j = JSON.ObjectFromURL(URLinfo, cacheTime=CACHE_1MONTH)
                    movie=j['data']['videos']
                    """
                    Set movie background art to screenshots or default background
                    Fetching backgrounds could slow down the browsing experience, Default: False
                    """
                    if Prefs['screenshots'] == True:
                        back = ""
                        if len(movie["screenshots"]) > 0:
                            back = movie["screenshots"][0]["url"]
                    else:
                        back = ""

                    movieId =  movie['id']
                    movieTitle =  movie["originalTitle"] 
                    movieSubtitle = "Price: %s" % (movie["price"])
                    movieSummary =  "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"]))
                    movieThumb = movie['posterUrl']
                    movieArt = back
           
                    # Check if the movie has a runtime 
                    if movie["runtime"] is None:
                        movieDuration = ""
                    else:
                        try:
                            int(movie["runtime"]) 
                        except ValueError:
                            movieDuration = ""
                        else:
                            movieDuration = movie["runtime"] * 60000
          
                    movieRating = float(movie['videoRatingAverage']) / 5 * 10
                    movieTrailer = movie['trailer']
                    moviePrice = movie['price']

                    dir.Append(
                        Function(
                            DirectoryItem(showMoviePopup,
                                title = movieTitle,
                                subtitle = movieSubtitle,
                                summary = movieSummary,
                                thumb = Callback(thumb, url = movieThumb),
                                duration =  movieDuration,
                                userRating = movieRating,
                                art = back
                            ), videoId = movieId, movieTitle = movieTitle, movieTrailer = movieTrailer, moviePrice = moviePrice, movieThumb = movieThumb, movieDuration = movieDuration, movieSummary = movieSummary, movieRating = movieRating  
                        )
                    )
                    if i == 100:
                        break
    return dir


def listMoviesInGenre(dir, browseType, category, sort, genre, offset, count):
    """
    Creates a MediaContainer with a list of Movies or Documentaries based on genre 

    @type dir: str
    @param dir: returned MediaContainer from openMovieGenre()

    @type browseType: str
    @param browseType:

    @type category: str
    @param category: browseType category

    @type sort: str
    @param sort: Sort by param

    @type genre: str
    @param genre: Show genre by param

    @type offset: int
    @param offset: Offset value

    @type count: int
    @param count: Count value 

    @rtype: str
    @return:
    """

    Log.Info('Listing genre: %s for: %s' % (genre, browseType))
    
    try:
        int(offset)
        int(count)
    except ValueError:
        Log.Exception('param offset and count needs to be an integers')
        return "param offset and count needs to be an integers"

    if Prefs['adultfilter'] == True:
        URL = API_META + "browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s&explicit=1" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))
    else:
        URL = API_META + "browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))

    try:
        # GET
        j = JSON.ObjectFromURL(URL)
    except Exception:
        Log.Exception('Failed to list movies or series')
        return MessageContainer("Failed to list movies or series", "Problem with communicating with Voddler\nPlease try again later")
    else:
        i = 0
        for movie in j["data"]["videos"]:
            """
            Set movie background art to screenshots or default background
            Fetching backgrounds could slow down the browsing experience, Default: False
            """
            if Prefs['screenshots'] == True:
                back = ""
                if len(movie["screenshots"]) > 0:
                    back = movie["screenshots"][0]["url"]
            else:
                back = ""

            movieId =  movie['id']
            movieTitle = removeUnsupportedChars(movie["originalTitle"])
            movieSubtitle = "Price: %s" % (movie["price"])
            movieThumb = movie['posterUrl']
            movieArt = back

            if movie["runtime"] is None:
                movieDuration = ""
            else:
                try:
                    int(movie["runtime"]) 
                except ValueError:
                    movieDuration = ""
                else:
                    movieDuration = movie["runtime"] * 60000

            movieRating = float(movie['videoRatingAverage']) / 5 * 10
            movieTrailer = movie['trailer']
            moviePrice = movie['price']         
 
            if browseType == "movie" or browseType == "documentary":
                i = i + 1
                
                """
                Checks if your specified subtitle is available or not
                """
                subLang = getSubtitleLang() 
                if len(movie["subtitles"]) > 0 and subLang != "Off":
                    for subs in movie["subtitles"]:
                        if subs["language"] == subLang: 
                            subs_available = "Yes"
                else:
                    subs_available = "No"            
                if subLang == "Off":
                    subs_available = "Off"

                movieSummary =  "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"]))

                dir.Append(
                    Function(
                        DirectoryItem(showMoviePopup,
                            title = movieTitle,
                            subtitle= movieSubtitle,
                            summary = movieSummary,
                            thumb =  Callback(thumb, url = movieThumb),
                            art = movieArt,
                            duration =  movieDuration,
                            userRating= movieRating
                        ), videoId = movieId, movieTitle = movieTitle, movieTrailer = movieTrailer, moviePrice = moviePrice, movieThumb = movieThumb, movieDuration = movieDuration, movieSummary = movieSummary, movieRating = movieRating 
                    )
                )

                # If more then count, append a next page
                if i == count:
                    offset = offset + count
                    dir.Append(
                        Function(
                            DirectoryItem(openMovieGenre,
                                title = "Next Page",
                                summary = "Next 100 Movies",
                                thumb = R(ICON) 
                            ),  genre = genre, browseType = browseType, offset = offset
                        )
                    ) 
            elif browseType == "series":
                dir.Append(
                    Function(
                        DirectoryItem(openTvShowsSeasons,
                            title = movieTitle,
                            subtitle = "",
                            summary = "Episodes: %s\nProduction year: %s" % (movie["numEpisodes"], movie["productionYear"]),
                            thumb = movieThumb,
                            duration = "", 
                            userRating = movieRating
                        ), seriesId = movie['id'], serieTitle = movie["originalTitle"] 
                    )
                )

    return dir


def listTvShowsSeasons(dir, seriesId, serieTitle):
    """
    Creates a MediaContainer with a list of TV Show seasons based on seriesId  

    @type dir:
    @param dir:

    @type seriesId:
    @param seriesId: Id of the series object

    @rtype:
    @return:
    """

    Log.Info('Listing TV Show seasons for: %s' % seriesId)

    URL = API_META + "seriesinfo/1?seriesId=" + seriesId
    try:
        # GET
        j = JSON.ObjectFromURL(URL, cacheTime=CACHE_1MONTH)
    except Exception:
        Log.Exception('Failed to list seasons')
        return MessageContainer("Failed to list seasons", "Problem with communicating with Voddler\nPlease try again later")
    else:
        seasons = {}
        for seasonNum, season in j["data"]["seasons"].items():
            seasonNum = int(seasonNum)
            season["num"] = seasonNum
            seasons[seasonNum] = season
        for season in seasons.values():
            dir.Append(
                Function(
                    DirectoryItem(openTvShowsEpisodes,
                        "Season %d" % season["num"],
                        subtitle= serieTitle, 
                        summary = "", 
                        thumb = R(ICON),
                        art=R(ART)
                    ), seasonNum = season["num"], seriesId=seriesId
                )
            )

    return dir


def listTvShowsEpisodes(dir, seasonNum, seriesId):
    """
    Creates a MediaContainer with a list of TV Show episodes based on seasonNum and seriesId

    @type dir:
    @param dir:

    @type seasonNum:
    @param seasonNum: Season of the series

    @type seriesId:
    @param seriesId: Id of the series object

    @rtype:
    @return:
    """

    Log.Info('Listing TV Show episodes for %s' % seriesId)

    URL = API_META + "seriesinfo/1?seriesId=" + seriesId
    try:
        # GET
        j = JSON.ObjectFromURL(URL, cacheTime=500)
    except Exception:
        Log.Exception('Failed to list seasons')
        return MessageContainer("Failed to list seasons", "Problem with communicating with Voddler\nPlease try again later")
    else:
        episodes = {}
        for episodeNum, episode in j["data"]["seasons"][str(seasonNum)].items():
            episodeNum = int(episodeNum)
            episode["num"] = episodeNum
            episodes[episodeNum] = episode
    
        for episode in episodes.values():
            URLinfo = API_META + "info/1?videoId=" +  episode["id"]
            # GET
            j = JSON.ObjectFromURL(URLinfo, cacheTime=CACHE_1MONTH)
            movie=j['data']['videos']
            """
            Sometimes the orginalTitle from seriesInfo is empty.
            If so, use the orginalTitle from Info instead
            """
            if episode["originalTitle"] == "" or episode["originalTitle"] == None:
                originalTitle = removeUnsupportedChars(movie["originalTitle"])
            else:
                originalTitle = removeUnsupportedChars(episode["originalTitle"])

            movieId =  movie['id']
            movieTitle =  originalTitle
            movieSubtitle = "Price: %s" % (movie["price"])
            movieSummary =  "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"]))
            movieThumb = movie['posterUrl']
           
            # Check if the movie has a runtime 
            if movie["runtime"] is None:
                movieDuration = ""
            else:
                try:
                    int(movie["runtime"]) 
                except ValueError:
                    movieDuration = ""
                else:
                    movieDuration = movie["runtime"] * 60000
          
            movieRating = float(movie['videoRatingAverage']) / 5 * 10
            movieTrailer = movie['trailer']
            moviePrice = movie['price']

            dir.Append(
                Function(
                    DirectoryItem(showMoviePopup,
                        title = "%d. %s" % (episode["num"], originalTitle),
                        subtitle = movieSubtitle,
                        summary = movieSummary,
                        thumb = movieThumb,
                        duration =  movieDuration,
                        userRating = movieRating
                    ), videoId = movieId, movieTitle = movieTitle, movieTrailer = movieTrailer, moviePrice = moviePrice, movieThumb = movieThumb, movieDuration = movieDuration, movieSummary = movieSummary, movieRating = movieRating 
                )
            )

    return dir


def openMovieGenre(sender, genre, browseType, offset=None):
    """
    Opens a Movie or TV Show genre.

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type genre: str
    @param genre: Opens a specific genre

    @type browseType: str
    @param browseType: Opens a specific browseType

    @rtype:
    @return:
    """

    Log.Info('Opening genre: %s for: %s' % (genre, browseType))
    filter = getFilterOptions()
    Log.Info('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log.Info('Sorting on %s' % sortorder)

    if offset == None:
        offset = 0

    dir = MediaContainer(viewGroup="WallStream", title2=sender.itemTitle)
    dir = listMoviesInGenre(dir, browseType, filter, sortorder, genre, offset, 100)

    if (len(dir) < 1):
        Log.Warn('Trying to access an empty genre')
        return MessageContainer(
            "Sorry",
            "Not available"
        )

    return dir


def openTvShowsSeasons(sender, seriesId, serieTitle):
    """
    Opens a list of Seasons for a specific TV Show

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type seriesId: int
    @param seriesId: Opens a specific serie

    @rtype:
    @return:
    """

    Log.Info('Opening Tv Show Seasons')
    filter = getFilterOptions()   
    Log.Info('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log.Info('Sorting on %s' % sortorder)

    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    dir = listTvShowsSeasons(dir, seriesId, serieTitle)

    if (len(dir) < 1):
        Log.Warn('Trying to access an empty tv show')
        return MessageContainer(
            "Sorry",
            "Not available"
        )

    return dir


def openTvShowsEpisodes(sender, seasonNum, seriesId):
    """
    Opens a TV Show Season.

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type seasonNum:
    @param seasonNum: Opens a specific season of serie

    @type seriesId: 
    @param seriesId: Opens a specific serie

    @rtype:
    @return:
    """

    Log.Info('Opening Tv Show Episodes')
    filter = getFilterOptions()
    Log.Info('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log.Info('Sorting on %s' % sortorder)

    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    dir = listTvShowsEpisodes(dir, seasonNum, seriesId)

    if (len(dir) < 1):
        Log.Warn('Trying to access an empty tv show season')
        return MessageContainer(
            "Sorry",
            "Not available"
        )

    return dir


def searchResults(sender,query=None):
    """
    Creates a MediaContainer with a list of Movies, Documentaries or TV Show episodes based on input from search. 

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type query:
    @param query: The specific search query
    
    @rtype: 
    @return:
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()

    if Prefs['username'] != None:
        validateUser()

    dir = MediaContainer(viewGroup="WallStream", title2=sender.itemTitle)
    Log.Info('Listing Search Results for: %s' % query)

    URL = API_META + "search/1?offset=0&count=" + Prefs['searchresults'] + "&q=" + String.Quote(query)
    try:
        # GET
        j = JSON.ObjectFromURL(URL, cacheTime=500)
    except Exception:
        Log.Exception('Failed to search')
        return MessageContainer("Failed to search", "Problem with communicating with Voddler\nPlease try again later")
    else:
        i = 0
        for movie in j["data"]["videos"]:
            i = i + 1
            """
            Set movie background art to screenshots or default background
            Fetching backgrounds could slow down the browsing experience, Default: False
            """
            if Prefs['screenshots'] == True:
                back = ""
                if len(movie["screenshots"]) > 0:
                    back = movie["screenshots"][0]["url"]
            else:
                back = ""

            movieId =  movie['id']
            movieTitle = removeUnsupportedChars(movie["originalTitle"])
            movieSubtitle = "Price: %s" % (movie["price"])
            movieSummary =  "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"]))
            movieThumb = movie['posterUrl']
            movieArt = back
           
            # Check if the movie has a runtime 
            if movie["runtime"] is None:
                movieDuration = ""
            else:
                try:
                    int(movie["runtime"]) 
                except ValueError:
                    movieDuration = ""
                else:
                    movieDuration = movie["runtime"] * 60000
          
            movieRating = float(movie['videoRatingAverage']) / 5 * 10
            movieTrailer = movie['trailer']
            moviePrice = movie['price']

            dir.Append(
                Function(
                    DirectoryItem(showMoviePopup,
                        title = movieTitle,
                        subtitle= movieSubtitle,
                        summary = movieSummary,
                        thumb =  Callback(thumb, url = movieThumb),
                        art = movieArt,
                        duration =  movieDuration,
                        userRating= movieRating
                    ), videoId = movieId, movieTitle = movieTitle, movieTrailer = movieTrailer, moviePrice = moviePrice, movieThumb = movieThumb, movieDuration = movieDuration, movieSummary = movieSummary, movieRating = movieRating
                )
            )

        if (i == 0):
            Log.Info('Did not find any result for %s' % query)
            return MessageContainer(
                "Search results",
                "Did not find any result for '%s'" % query
            )

    return dir


def showMoviePopup(sender, videoId, movieTitle, movieTrailer, moviePrice, movieThumb, movieDuration, movieSummary, movieRating):
    """
    Creates a MediaContainer (popup menu) for a videoItem

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type videoId:
    @param videoId: Id of the video object

    @type trailerURL:
    @param trailerURL: URL to the trailer of the movie 

    @type price:
    @param price: The price of the movie

    @type thumb:
    @param thumb: Thumbnail URL

    @type runtime:
    @param runtime: The runtime of the movie, in milliseconds
    
    @rtype:
    @return: 
    """

    Log.Info('Showing popup menu for: %s' % videoId)
    Log.Info('thumb: %s' % thumb)
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)

    """ 
    if the movie is AVOD, then always allow access to the user
    if the movie is not AVOD, verify with the user session if the user has access or not
    """
    if moviePrice != "Free":
        URL = API_USER + "access/1"
        try:
            # POST
            g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId'], 'videoId': videoId}, cacheTime=5)
        except Exception:
            Log.Exception('Failed to get session')
            return MessageContainer("Failed to get session", "Problem with communicating with Voddler\nPlease try again later")
        else:
            if g['data']['hasAccess'] == True:

                try:
                    vnet_session = getVnetSession()
                except Exception:
                    Log.Exception('Failed to get vnet session')
                    return MessageContainer("Failed to get vnet session", "Problem with communicating with Voddler\nPlease try again later")
                else:
         
                    # Check if resume point is available or not
                    URL = API_VNET + "index/pre-movie-request/"
                    try:
                        # POST
                        resume = XML.ObjectFromURL(URL, values={'crid': '0', 'movie': videoId, 'session': vnet_session, 'version': '3'}, cacheTime=5)
                    except Exception:
                        Log.Exception('Failed to get resume point')
                        return MessageContainer("Failed to get resume point", "Problem with communicating with Voddler\nPlease try again later")
                    else:
                        vnet_resume = resume.xpath('/result/resume/@timecode')
                        vnet_resume = int(vnet_resume[0])
                        Log.Info('vnet resume: %s' % vnet_resume)

                if vnet_resume < 10:
                    dir.Append(
                        Function(
                            WebVideoItem(playVideo, 
                                title = movieTitle,
                                subtitle = "Play Movie",
                                summary = movieSummary,
                                thumb = movieThumb,
                                userRating = movieRating,
                                duration = movieDuration
                            ), videoId = videoId, resume = True
                        )
                    )
                    Log.Info('No resume point found, start movie from the start')
                else:
                    Log.Info('Resume point found, starting movie from: %s' % vnet_resume)
                    dir.Append(
                        Function(
                            PopupDirectoryItem(showResumeOptions, 
                                title = "Play Movie",
                                subtitle = movieTitle,
                                summary = movieSummary,
                                thumb = movieThumb,
                                userRating = movieRating,
                                duration = movieDuration
                            ), videoId = videoId
                        )
                    )
            else:
                dir.Append(
                    Function(
                        DirectoryItem(listPaymentOptions,
                            title = "Rent Movie",
                            subtitle = movieTitle,
                            summary = movieSummary,
                            thumb = movieThumb,
                            duration = movieDuration,
                            userRating = movieRating
                       ), videoId = videoId
                    )
                )
    else:
        try:
            vnet_session = getVnetSession()
        except Exception:
            Log.Exception('Failed to get vnet session')
            return MessageContainer("Failed to get vnet session", "Problem with communicating with Voddler\nPlease try again later")
        else:
         
            # Check if resume point is available or not
            URL = API_VNET + "index/pre-movie-request/"
            try:
                # POST
                resume = XML.ObjectFromURL(URL, values={'crid': '0', 'movie': videoId, 'session': vnet_session, 'version': '3'}, cacheTime=3)
            except Exception:
                Log.Exception('Failed to get resume point')
                return MessageContainer("Failed to get resume point", "Problem with communicating with Voddler\nPlease try again later")
            else:
                vnet_resume = resume.xpath('/result/resume/@timecode')
                vnet_resume = int(vnet_resume[0])
                Log.Info('vnet resume: %s' % vnet_resume)

        if vnet_resume < 10:
            dir.Append(
                Function(
                    WebVideoItem(playVideo, 
                        title = "Play Movie",
                        subtitle = movieTitle,
                        summary = movieSummary,
                        thumb = movieThumb,
                        userRating = movieRating,
                        duration = movieDuration
                   ), videoId = videoId, resume = True
                )
            )
            Log.Info('No resume point found, start movie from the start')
        else:
            Log.Info('Resume point found, starting movie from: %s' % vnet_resume)
            dir.Append(
                Function(
                    PopupDirectoryItem(showResumeOptions, 
                        title = "Play Movie",
                        subtitle = movieTitle,
                        summary = movieSummary,
                        thumb = movieThumb,
                        userRating = movieRating,
                        duration = movieDuration
                   ), videoId = videoId
                )
            )

    """
    if the param trailerURL has a value then allow access to the trailer
    some trailer urls are bad, so just do a simple urlparse check
    """
    if movieTrailer != None:
        o = urlparse(movieTrailer)
        if o.scheme == "http":
            Log.Info('trailerurl: %s' % movieTrailer)
            dir.Append(
                VideoItem(movieTrailer,
                    title = "Play Trailer",
                    subtitle = "Play Trailer",
                    summary = movieSummary,
                    thumb = R('plex_icon_trailer.png'),
                    duration = ""
                )
            )
    """
    get the user playlistIds from the session
    check if the param videoId is available in the playlist or not
    return correct values if video needs to be added or removed to modifyPlaylist()
    """
    URL = API_USER + "playlists/1"
    try:
        # POST
        g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId']}, cacheTime=5)
    except Exception:
        Log.Exception('Failed to get session')
        return MessageContainer("Failed to get session", "Problem with communicating with Voddler\nPlease try again later")
    else:
        for p in g["data"]["playlists"]:
            if p["type"] == "favorites":
                playlistId = p['id']
                videoExists = False
                for v in p["videos"]:
                    if v['id'] == videoId:
                        videoExists = True
                if videoExists == True:
                    dir.Append(
                        Function(
                            DirectoryItem(modifyPlaylist,
                                title="Remove from Favorites", 
                                subtitle= "",
                                summary = "",
                                thumb = R('plex_icon_favorites.png'),
                                duration =  "",
                                userRating= "",
                            ), videoId = videoId, playlistId = playlistId, modify = "del" 
                        )
                    )
                elif videoExists == False:
                    dir.Append(
                        Function(
                            DirectoryItem(modifyPlaylist,
                                title="Add to Favorites", 
                                subtitle= "",
                                summary = "",
                                thumb = R('plex_icon_favorites.png'),
                                duration =  "",
                                userRating= "",
                            ), videoId = videoId, playlistId = playlistId, modify = "add" 
                        )
                    )
            if p["type"] == "playlist":
                playlistId = p['id']
                videoExists = False
                for v in p["videos"]:
                    if v['id'] == videoId:
                        videoExists = True
                if videoExists == True:
                    dir.Append(
                        Function(
                            DirectoryItem(modifyPlaylist,
                                title="Remove from Playlist", 
                                subtitle= "",
                                summary = "",
                                thumb = R('plex_icon_playlist.png'),
                                duration =  "",
                                userRating= "",
                            ), videoId = videoId, playlistId = playlistId, modify = "del" 
                        )
                    )
                elif videoExists == False:
                    dir.Append(
                        Function(
                            DirectoryItem(modifyPlaylist,
                                title="Add to Playlist", 
                                subtitle= "",
                                summary = "",
                                thumb = R('plex_icon_playlist.png'),
                                duration =  "",
                                userRating= "",
                            ), videoId = videoId, playlistId = playlistId, modify = "add" 
                        )
                    )
    return dir


def showResumeOptions(sender, videoId):
    """
    Lists video resume options
 
    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type videoId:
    @param videoId: Id of the video object

    @rtype:
    @return:
    """

    Log.Info('Showing resume menu for: %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)

    dir.Append(
        Function(
             WebVideoItem(playVideo,
                title = "Resume Movie",
                subtitle = "",
                summary = "",
                thumb = "",
                duration = "",
                userRating= "",
                art = ""
            ), videoId = videoId, resume = True
        )
    )
    dir.Append(
        Function(
             WebVideoItem(playVideo,
                title = "Restart Movie",
                subtitle = "",
                summary = "",
                thumb = "",
                duration = "",
                userRating= "",
                art = ""
            ), videoId = videoId, resume = False
        )
    )

    return dir


def modifyPlaylist(sender, videoId, playlistId, modify):
    """
    Adds or Removes a videoItem in a playlist

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type videoId: 
    @param videoId: Id of the video object 

    @type playlistId:
    @param playlistId: Id of the playlist object

    @type modify:
    @param modify: Information about how a playlist should be modified

    @rtype:
    @return: A MessageContainer with return status
    """

    if modify == "add":
        URL = API_USER + "playlistadd/1"
        try:
            g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId'],'playlist': playlistId,'video': videoId}, cacheTime=5)
        except Exception:
                Log.Exception('Error')
                return MessageContainer("Failed to add video", "Problem with communicating with Voddler\nPlease try again later")
        else:
            if g['message'] != "Added" or g['success'] != True:
                Log.Error('Error, Video was not added to your playlist')
                mc = MessageContainer("Error", "Video was not added to your playlist")
            else:
                Log.Info('Video: %s was added to playlist: %s' % (videoId, playlistId))
                mc = MessageContainer("Success", "Video added to playlist") 
     
    elif modify == "del":
        URL = API_USER + "playlistremove/1"
        try:
            g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId'],'playlist': playlistId,'video': videoId}, cacheTime=5)
        except Exception:
            Log.Exception('Failed to get session')
            return MessageContainer("Failed to remove video", "Problem with communicating with Voddler\nPlease try again later")
        else:
            if g['message'] != "Removed" or g['success'] != True:
               Log.Error('Error, Video was not removed from your playlist')
               mc = MessageContainer("Error", "Video was not removed from your playlist")
            else:
               Log.Info('Video: %s was added to playlist: %s' % (videoId, playlistId))
               mc = MessageContainer("Success", "Video was removed from your playlist") 

    else:
        Log.Exception('Error, Unkown modify tag')
        mc = MessageContainer("Error", "Unknown modify tag")

    return mc 


def listPaymentOptions(sender, videoId):
    """
    Lists available payment options
 
    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type videoId:
    @param videoId: Id of the video object

    @rtype:
    @return:
    """

    Log.Info('Showing voucher menu for: %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)

    URL = API_PAYMENT + "v1/options/rent/" + videoId + "/?session=" + Dict['sessionId']
    try:
        # GET (should be POST)
        g = JSON.ObjectFromURL(URL, cacheTime=20)
    except Exception:
        Log.Exception('Failed to get payment data')
        return MessageContainer("Failed to get payment data", "Problem with communicating with Voddler\nPlease try again later")
    else:
        """
        get all paymentmethods available for this purchase
        """
        for methods in g["data"]["methods"]:
            """
            premium vouchers available?
            """
            if methods['name'] == "premium_voucher":
                dir.Append(
                    Function(
                        DirectoryItem(listVouchers,
                            title = "Rent using a Premium Voucher",
                            subtitle = "Premium Voucher",
                            summary = "",
                            thumb = R('plex_icon_voucher.png'),
                            duration = "",
                            userRating= "",
                            art = ""
                        ), videoId = videoId
                    )
                )
        
        dir.Append(
            Function(
                InputDirectoryItem(makePayment,
                    "Rent using a Ticket Code",
                    "Enter The Ticket Code",
                    summary = "",
                    thumb = R('plex_icon_voucher.png'),
                    art = "",
                ), videoId = videoId, paymentMethod = "voucher"
            )
        ) 

    return dir


def listVouchers(sender, videoId):
    """
    Lists available vouchers
 
    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type videoId:
    @param videoId: Id of the video object

    @rtype:
    @return:
    """

    Log.Info('Showing voucher menu for: %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)

    URL = API_PAYMENT + "v1/options/rent/" + videoId + "/?session=" + Dict['sessionId']
    try:
        # GET (should be POST)
        g = JSON.ObjectFromURL(URL, cacheTime=20)
    except Exception:
        Log.Exception('Failed to get voucher data')
        return MessageContainer("Failed to get voucher data", "Problem with communicating with Voddler\nPlease try again later")
    else:
        """
        get all paymentmethods available for this purchase
        """
        for methods in g["data"]["methods"]:
            """
            premium vouchers available?
            """
            if methods['name'] == "premium_voucher":
                for vouchers in methods["extra"]["vouchers"]:
                    voucherExpire = time.strftime("%D %H:%M", time.localtime(int(vouchers["campaign"]["endDate"])))
                    dir.Append(
                        Function(
                            DirectoryItem(makePayment,
                                title = "%s" % (vouchers["campaign"]["title"]),
                                subtitle = "Premium Voucher",
                                summary = "voucherKey: %s\nExpires: %s" % (vouchers["voucherKey"], voucherExpire),
                                thumb = R('plex_icon_voucher.png'),
                                duration = "",
                                userRating = "",
                                art = ""
                            ), videoId = videoId, paymentMethod = "premium_voucher", voucherKey = vouchers["voucherKey"] 
                        )
                    )
    return dir


def makePayment(sender, videoId, paymentMethod, voucherKey=None, query=None):
    """
    Rent a movie with a specific payment option.

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type videoId:
    @param videoId: Id of the video object

    @type paymentMethod:
    @param paymentMethod: The payment option provided, voucher and premium_vouchers are allowed.

    @type voucherKey:
    @param voucherKey: The voucherKey if provided

    @type query:
    @param query: The voucherKey based on input if provided

    @rtype:
    @return:
    """

    Log.Info('paymentMethod used: %s' % paymentMethod)

    if paymentMethod == "premium_voucher" or paymentMethod == "voucher":
      
        if paymentMethod == "voucher": 
            if query != None:
                voucherKey = query
            else:
                Log.Exception('Error, Unkown voucherKey from query')
        
        Log.Info('videoId: %s voucherKey: %s' % (videoId, voucherKey))
        URL = API_PAYMENT + "v1/submit/rent/" + videoId
        try:
            # POST
            g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId'],'method': paymentMethod,'voucher': voucherKey}, cacheTime=5)
        except Exception:
                Log.Exception('Error')
                return MessageContainer("Failed to rent video", "Problem with communicating with Voddler\nPlease try again later")
        else:
            if g['success'] == True:
                Log.Info('Rented video: %s with voucher: %s' % (videoId, voucherKey))
                mc = MessageContainer("Success", "Video now available")
            else:
                Log.Error('Error, Failed to rent video')
                mc = MessageContainer("Failed to rent video", "There was an issue with the voucher\nPlease try again later") 

    else:
        Log.Exception('Error, Unkown payment type')
        mc = MessageContainer("Error", "Unknown payment type") 

    return mc


def removeHtmlTags(text):
    """
    Removes wierd tags and non unicode characters from synopsis text.

    @type text: str
    @param text: synopsis from videoId.
    
    @rtype: str
    @return: Formated text 
    """

    p = re.compile(r'<[^<]*?/?>')
    text = p.sub('', text)
    text = text.replace("\r","")
    text = text.replace("\n","")
    text = text.replace("&amp;","")
    text = text.replace("nbsp;","")
    p = re.compile(r'(?<=[a-z])[\r\n]+')
    text = p.sub('', text)

    # sometimes other wierd characters make a mess
    p = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    text = p.sub('', text)

    return text


def removeUnsupportedChars(text):
    """
    Remove wierd non unicode characters from text

    @type text: str
    @param text: 

    @rtype: str
    @return: Formated text
    """

    p = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    text = p.sub('', text)

    return text



def addSearch(dir):
    """
    Adds a seearch directory item

    @type dir:
    @param dir:
    """

    dir.Append(
        Function(
            InputDirectoryItem(searchResults,
                Locale.LocalString('menu_Search'),
                "Search for films, actors, directors, writers and more",
                summary="Search for films, actors, directors, writers and more",
                thumb=R('plex_icon_search.png'),
                art=R(ART)
            )
        )
    )


def playVideo(sender, videoId, resume):
    """
    Performs some checks and sets the correct subtitle
    Returns an URL with a resume point or not

    @type sender:
    @param sender:

    @type videoId:
    @param videoId:

    @type resume:
    @param resume: If the movie should resume or not

    @rtype:
    @return:
    """

    Log.Info('Trying to play video with ID: %s' % videoId)

    # Set correct subtitle
    setSubtitle()

    MOVIE_URL = API_PLAY + "embedded/1?videoId=" + videoId + "&session=" + Dict["sessionId"] + "&format=html&plex=1&wmode=opaque"

    # Resume or not?
    if resume == True:
        MOVIE_URL = MOVIE_URL + "resume=1"
    else:
        MOVIE_URL = MOVIE_URL + "resume=0" 
 
    return Redirect(
               WebVideoItem(
                   MOVIE_URL
               )  
           )

def thumb(url):
    """
    Gets the thumbnail URL, cache the object and redirect a thumbnail icon

    @type url:
    @param url:

    @rtype:
    @return:
    """

    try:
        data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
        return DataObject(data, 'image/jpeg')
    except:
        pass
    
    return Redirect(R(ICON))

