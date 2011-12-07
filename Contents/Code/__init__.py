# -*- encoding: utf-8

import re

############################################################################################

VERSION        = "1.5"
VIDEO_PREFIX   = "/video/voddler"
NAME           = L('Title')
ART            = 'art-default.jpg'
ICON           = 'icon-default.png'

API_META       = 'https://api.voddler.com/metaapi/'
API_USER       = 'https://api.voddler.com/userapi/'
API_PAYMENT    = 'https://api.voddler.com/paymentapi/'

NO_ITEMS       = MessageContainer('No Results','No Results')
TRY_AGAIN      = MessageContainer('Error','An error has happened. Please try again later.')
ERROR          = MessageContainer('Network Error','A Network error has occurred')

############################################################################################

def ValidatePrefs():
    """
    Validates prefrences.

    """

    u = Prefs['username']
    p = Prefs['password']
    if( u == None or p == None ):
        return MessageContainer(
            "Error",
            "You need to provide a username and password to use this service"
        )


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
    Prefs.SetDialogTitle("Preferences for Voddler")
    #HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'
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
    dir.Append(
        Function(
            InputDirectoryItem(searchResults,
                "Search",
                "Search",
                summary="Search for films, actors, directors, writers and more",
                thumb=R('plex_icon_search.png'),
                art=R(ART)
            )
        )
    )
    # list movie genres
    dir.Append(
        Function(
            DirectoryItem(listMovieGenres,
                "Movies",
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
                "TV Shows",
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
                "Documentaries",
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
                "Favorites",
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
                "Playlist",
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
                "History",
                subtitle="",
                summary="All the Voddler movies and episodes you have watched",
                thumb=R('plex_icon_history.png'),
                art=R(ART)
            ), playlistType = "history"
        )
    )
    # preference tab
    dir.Append(
        PrefsItem(
            title="Preferences",
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
    dir = MediaContainer(viewGroup="InfoList")

    URL = API_META + "genres/1?type=" + genreCategory
    try:
        # GET
        g = JSON.ObjectFromURL(URL)
    except Exception:
        Log.Exception('Failed to list genres')
        return MessageContainer("Failed to list genres", "Problem with communicating with Voddler\nPlease try again later")
    else:
        """
            dir.Append Search to the output
        """        
        dir.Append(
            Function(
                InputDirectoryItem(searchResults,
                    "Search",
                    "Search",
                    summary="Search for films, actors, directors, writers and more",
                    thumb=R('plex_icon_search.png'),
                    art=R(ART)
                )
            )
        )
        """
            fetch all genre data
            add or disregard the adult genres
            dir.Append items with the correct browseType 
        """
        for genre in g['data']:
            # Verify AdultFilter
            if Prefs['adultfilter'] == False:
                if genre["value"] == "explicit":
                    continue
            dir.Append(
                Function(
                    DirectoryItem(openMovieGenre,
                        genre['name'],
                        subtitle="",
                        summary="",
                        thumb=R(ICON),
                        art=R(ART)
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
    dir = MediaContainer(viewGroup="WallStream")

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
                for v in p["videos"]:
                    # get all information for specific video
                    URLinfo = API_META + "info/1?videoId=" + v['id']
                    # GET
                    j = JSON.ObjectFromURL(URLinfo, cacheTime=500)
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

                    dir.Append(
                        Function(
                            PopupDirectoryItem(showMoviePopup,
                                movie["originalTitle"],
                                subtitle= "Price: %s" % (movie["price"]),
                                summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                                thumb = movie["posterUrl"],
                                duration =  movie["runtime"],
                                userRating=float(movie['videoRatingAverage']) / 5 * 10,
                                art=back
                            ), videoId = movie['id'], trailerURL = movie['trailer'], price = movie['price']
                        )
                    )
    
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

            if browseType == "movie" or browseType == "documentary":
                dir.Append(
                    Function(
                        PopupDirectoryItem(showMoviePopup,
                            movie["originalTitle"],
                            subtitle = "Price: %s" % (movie["price"]),
                            summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                            thumb = movie["posterUrl"],
                            art = back,
                            duration =  movie["runtime"],
                            userRating = float(movie['videoRatingAverage']) / 5 * 10
                        ), videoId = movie['id'], trailerURL = movie['trailer'], price = movie['price']
                    )
                )
            elif browseType == "series":
                dir.Append(
                    Function(
                        DirectoryItem(openTvShowsSeasons,
                            title= movie["originalTitle"],
                            subtitle="",
                            summary = "Episodes: %s\nProduction year: %s" % (movie["numEpisodes"], movie["productionYear"]),
                            thumb = movie["posterUrl"],
                            duration ="", 
                            userRating=float(movie['videoRatingAverage']) / 5 * 10
                        ), seriesId = movie['id']
                    )
                )

            if (i == count):
                offset = offset + count
                dir = listMoviesInGenre(dir, browseType, category, sort, genre, offset, count)

    return dir


def listTvShowsSeasons(dir, seriesId):
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
    dir = MediaContainer(viewGroup="InfoList")

    URL = API_META + "seriesinfo/1?seriesId=" + seriesId
    try:
        # GET
        j = JSON.ObjectFromURL(URL)
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
                        subtitle= "", 
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
    dir = MediaContainer(viewGroup="InfoList")

    URL = API_META + "seriesinfo/1?seriesId=" + seriesId
    try:
        # GET
        j = JSON.ObjectFromURL(URL)
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
            j = JSON.ObjectFromURL(URLinfo, cacheTime=500)
            movie=j['data']['videos']
            """
            Sometimes the orginalTitle from seriesInfo is empty.
            If so, use the orginalTitle from Info instead
            """
            if episode["originalTitle"] == "" or episode["originalTitle"] == None:
                originalTitle = movie["originalTitle"]
            else:
                originalTitle = episode["originalTitle"]

            dir.Append(
                Function(
                    PopupDirectoryItem(showMoviePopup,
                        title="%d. %s" % (episode["num"], originalTitle),
                        subtitle= "Price: %s" % (movie["price"]),
                        summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                        thumb = "",
                        duration =  movie["runtime"],
                        userRating=float(movie['videoRatingAverage']) / 5 * 10
                    ), videoId = movie['id'], trailerURL = movie['trailer'], price = movie['price']
                )
            )

    return dir


def openMovieGenre(sender, genre, browseType):
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

    dir = MediaContainer(viewGroup="WallStream")
    dir = listMoviesInGenre(dir, browseType, filter, sortorder, genre, 0, 200)

    if (len(dir) < 1):
        Log.Warn('Trying to access an empty genre')
        return MessageContainer(
            "Sorry",
            "Not available"
        )

    return dir


def openTvShowsSeasons(sender, seriesId):
    """
    Opens a list of Seasons for a specific TV Show

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about
                   the previous window state and the item that initiated the function call.

    @type seriesId: int
    @param seriesId: Opens a specific serie

    @type browseType: str
    @param browseType: Opens a specific browseType

    @rtype:
    @return:
    """

    Log.Info('Opening Tv Show Seasons')
    filter = getFilterOptions()   
    Log.Info('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log.Info('Sorting on %s' % sortorder)

    dir = MediaContainer(viewGroup="WallStream")
    dir = listTvShowsSeasons(dir, seriesId)

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

    @type browseType: str
    @param browseType: Opens a specific browseType

    @rtype:
    @return:
    """

    Log.Info('Opening Tv Show Episodes')
    filter = getFilterOptions()
    Log.Info('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log.Info('Sorting on %s' % sortorder)

    dir = MediaContainer(viewGroup="WallStream")
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

    dir = MediaContainer(viewGroup="InfoList")
    Log.Info('Listing Search Results for: %s' % query)

    URL = API_META + "search/1?offset=0&count=20&q=" + String.Quote(query)
    try:
        # GET
        j = JSON.ObjectFromURL(URL)
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
            dir.Append(
                Function(
                    PopupDirectoryItem(showMoviePopup,
                        movie["originalTitle"],
                        subtitle= "Price: %s" % (movie["price"]),
                        summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                        thumb = movie["posterUrl"],
                        art = back,
                        duration =  movie["runtime"],
                        userRating=float(movie['videoRatingAverage']) / 5 * 10
                    ), videoId = movie['id'], trailerURL = movie['trailer'], price = movie['price']
                )
            )

        if (i == 0):
            Log.Info('Did not find any result for %s' % query)
            return MessageContainer(
                "Search results",
                "Did not find any result for '%s'" % query
            )

    return dir


def showMoviePopup(sender, videoId, trailerURL, price):
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
    
    @rtype:
    @return: 
    """

    Log.Info('Showing popup menu for: %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList")

    """ 
    if the movie is AVOD, then always allow access to the user
    if the movie is not AVOD, verify with the user session if the user has access or not
    """
    MOVIE_URL = "http://www.voddler.com/playapi/embedded/1?videoId=" + videoId + "&session=" + Dict["sessionId"] + "&format=html&plex=1&wmode=opaque"
    if price != "Free":
        URL = API_USER + "access/1"
        try:
            # POST
            g = JSON.ObjectFromURL(URL, values={'session': Dict['sessionId'], 'videoId': videoId}, cacheTime=5)
        except Exception:
            Log.Exception('Failed to get session')
            return MessageContainer("Failed to get session", "Problem with communicating with Voddler\nPlease try again later")
        else:
            if g['data']['hasAccess'] == True:
                dir.Append(
                    WebVideoItem(MOVIE_URL,
                        title= "Play Movie",
                        subtitle="",
                        summary="",
                        thumb="",
                        duration= "",
                        userRating="",
                        art=""
                    )
                )
            else:
                dir.Append(
                    Function(
                        PopupDirectoryItem(listVouchers,
                            title= "Rent Movie with ticket",
                            subtitle="",
                            summary="",
                            thumb="",
                            duration= "",
                            userRating="",
                            art=""
                       ), videoId = videoId
                    )
                )
    else:
        dir.Append(
            WebVideoItem(MOVIE_URL,
                title= "Play Movie",
                subtitle="",
                summary="",
                thumb="",
                duration= "",
                userRating="",
                art=""
            )
        )
    """
    if the param trailerURL has a value then allow access to the trailer
    """
    if trailerURL != None:
        dir.Append(
            VideoItem(trailerURL,
                title= "Play Trailer",
                subtitle="",
                summary="",
                thumb="",
                duration= "",
                userRating="",
                art=""
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
                                thumb = "",
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
                                thumb = "",
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
                                thumb = "",
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
                                thumb = "",
                                duration =  "",
                                userRating= "",
                            ), videoId = videoId, playlistId = playlistId, modify = "add" 
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


def listVouchers(sender, videoId):
    """
    Lists available vouchers
 
    @type sender:
    @param sender:

    @type videoId:
    @param videoId:
    """

    Log.Info('Showing voucher menu for: %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList")

    URL = API_PAYMENT + "v1/options/rent/" + videoId + "/?session=" + Dict['sessionId']
    try:
        g = JSON.ObjectFromURL(URL)
    except Exception:
        Log.Exception('Failed to get voucher data')
        return MessageContainer("Failed to get voucher data", "Problem with communicating with Voddler\nPlease try again later")
    else:
        for p in g["data"]["methods"]:
            Log.Info('output: %s' % p)


         """

         WIP


         {
            "message": "",
             "data":
            {
                "methods":
                [
                    {
                        "name": "voucher"
                    },

                    {
                        "name": "premium_voucher",
                         "extra":
                        {
                            "vouchers":
                            [
                                {
                                    "status":"created",
                                     "endDate": null,
                                     "voucherKey": "84BCA8ED22534AA",
                                     "campaign":
                                    {
                                        "publishers": [],
                                         "genres": [],
                                         "endDate": 1350086400,
                                         "title": "PaymentTest1",
                                         "deleted": false,
                                         "type": "gold",
                                         "promoPage": null,
                                         "startDate": 1304294400,
                                         "period": 0,
                                         "active": true,
                                         "partOfSubscription": false,
                                         "markets": [],
                                         "id": "2801199048651018503",
                                         "showTicketsLeft": true
                                    },
                                    "campaignId": "2801199048651018503",
                                     "usedDate": null,
                                     "userId": "2721821230486141888",
                                     "createdDate": 1304604109,
                                     "id": "2801199048651018639"
                                },
                            ]
                        }
                    }
                ]
            },
             "success": true
        }
        """

            dir.Append(
                Function(
                   PopupDirectoryItem(makePayment,
                        #title= "Use ticket: %s" % (p["voucherKey"]),
                        title= "Rent Movie with ticket",
                        subtitle="",
                        summary="",
                        thumb="",
                         duration= "",
                         userRating="",
                         art=""
                    ), videoId = videoId #, voucherKey = p["voucherKey"] 
                )
            )

    return dir


def makePayment(videoId, voucherKey):
    """
    Rent a movie with a specified voucher

    @type videoId:
    @param videoId:

    @type voucherKey:
    @param voucherKey:
    """

    return MessageContainer("Test", "Work in progresses")


def removeHtmlTags(text):
    """
    Removes wierd tags from synopsis text.

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
    return text

