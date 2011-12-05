# -*- encoding: utf-8
#
# Voddler Plex Plugin
#

import re

VERSION        = "1.4"
VIDEO_PREFIX   = "/video/voddler"
NAME           = L('Title')
ART            = 'art-default.jpg'
ICON           = 'icon-default.png'

API_META       = 'https://api.voddler.com/metaapi/'
API_USER       = 'https://api.voddler.com/userapi/'

NO_ITEMS       = MessageContainer('No Results','No Results')
TRY_AGAIN      = MessageContainer('Error','An error has happened. Please try again later.')
ERROR          = MessageContainer('Network Error','A Network error has occurred')


#####################################################################################


def ValidatePrefs():
    """
    Validates prefrences.

    """

    u = Prefs['username']
    p = Prefs['password']
    f = Prefs['filter']
    if( u == None or p == None or f == None):
        return MessageContainer(
            "Error",
            "You need to provide a username and password to use this service"
        )


def getFilterOptions():
    """
    Returning filter preferences.

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
    Returning sorting preferences.

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
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

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
        #URL = "https://api.voddler.com/userapi/login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        URL = API_USER + "login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    Log.Info('Listing genres for: %s' % genreCategory)
    dir = MediaContainer(viewGroup="InfoList")
    # add search to list
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
    URL = API_META + "genres/1?type=" + genreCategory
    g = JSON.ObjectFromURL(URL)
    for genre in g['data']:
        # show adult genre or not
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
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.
    
    @type playlistType: str
    @param playlistType: Type playlist you want to return
    
    @rtype dir:
    @return dir: MediaContainer with options
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = API_USER + "login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    Log.Info('Listing Playlist: %s' % playlistType)
    dir = MediaContainer(viewGroup="WallStream")
    URL = API_USER + "playlists/1?session=" + Dict['sessionId']
    g = JSON.ObjectFromURL(URL, cacheTime=5)
    for p in g["data"]["playlists"]:
        if p["type"] == playlistType:
            for v in p["videos"]:
                # get all information for specific video
                URLinfo = API_META + "info/1?videoId=" + v['id']
                j = JSON.ObjectFromURL(URLinfo)
                movie=j['data']['videos']
                back = "";
                if len(movie["screenshots"]) > 0:
                    back = movie["screenshots"][0]["url"]
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
    if Prefs['adultfilter'] == True:
        URL = API_META + "browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s&explicit=1" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))
    else:
        URL = API_META + "browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))
    if browseType == "movie" or browseType == "documentary":
        j = JSON.ObjectFromURL(URL)
        i = 0
        for movie in j["data"]["videos"]:
            i = i + 1
            back = "";
            if len(movie["screenshots"]) > 0:
                back = movie["screenshots"][0]["url"]
            dir.Append(
                Function(
                    PopupDirectoryItem(showMoviePopup,
                        movie["originalTitle"],
                        subtitle = "Price: %s" % (movie["price"]),
                        summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                        thumb = movie["posterUrl"],
                        duration =  movie["runtime"],
                        userRating = float(movie['videoRatingAverage']) / 5 * 10
                    ), videoId = movie['id'], trailerURL = movie['trailer'], price = movie['price']
                )
            )
        if (i == count):
            offset = offset + count
            dir = listMoviesInGenre(dir, browseType, category, sort, genre, offset, count)
    if browseType == "series":
        j = JSON.ObjectFromURL(URL)
        i = 0
        for movie in j["data"]["videos"]:
            i = i + 1
            dir.Append(
                Function(
                    DirectoryItem(openTvShowsSeasons,
                        title= movie["originalTitle"],
                        subtitle="",
                        summary = "Episodes: %s\nProduction year: %s" % (movie["numEpisodes"], movie["productionYear"]),
                        thumb = movie["posterUrl"],
                        duration ="", 
                        userRating=float(movie['videoRatingAverage']) / 5 * 10
                    ), seriesId = movie['id'], browseType=browseType
                )
            )
        if (i == count):
            offset = offset + count
            dir = listMoviesGenre(dir, browseType, category, sort, genre, offset, count)  
    return dir


def listTvShowsSeasons(dir, browseType, category, sort, seriesId, offset, count):
    """
    Creates a MediaContainer with a list of TV Show seasons based on seriesId  

    @type dir:
    @param dir:

    @type browseType
    @param browseType:

    @type category:
    @param category:

    @type sort:
    @param sort:

    @type seriesId:
    @param seriesId:

    @type offset:
    @param offset:

    @type count:
    @param count:

    @rtype:
    @return:
    """

    Log.Info('Listing TV Show seasons for: %s' % seriesId)
    dir = MediaContainer(viewGroup="InfoList")
    URL = API_META + "seriesinfo/1?seriesId=" + seriesId
    j = JSON.ObjectFromURL(URL)
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
                    summary = "", #
                    thumb = R(ICON),
                    art=R(ART)
                ), seasonNum = season["num"], seriesId=seriesId, browseType=browseType
            )
        )
    return dir


def listTvShowsEpisodes(dir, browseType, category, sort, seasonNum, seriesId, offset, count):
    """
    Creates a MediaContainer with a list of TV Show episodes based on seasonNum and seriesId

    @type dir:
    @param dir:

    @type browseType
    @param browseType:

    @type category:
    @param category:

    @type sort:
    @param sort:

    @type seasonNum:
    @param seasonNum:

    @type seriesId:
    @param seriesId:

    @type offset:
    @param offset:

    @type count:
    @param count:

    @rtype:
    @return:
    """

    Log.Info('Listing TV Show episodes for %s' % seriesId)
    dir = MediaContainer(viewGroup="InfoList")
    URL = API_META + "seriesinfo/1?seriesId=" + seriesId
    j = JSON.ObjectFromURL(URL)
    episodes = {}
    for episodeNum, episode in j["data"]["seasons"][str(seasonNum)].items():
        episodeNum = int(episodeNum)
        episode["num"] = episodeNum
        episodes[episodeNum] = episode
    
    for episode in episodes.values():
        URLinfo = API_META + "info/1?videoId=" +  episode["id"]
        j = JSON.ObjectFromURL(URLinfo)
        movie=j['data']['videos']
        # If orginalTitle from seriesInfo is empty, use the orginalTitle from Info instead
        if episode["originalTitle"] == "" or episode["originalTitle"] == "null":
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
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

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


def openTvShowsSeasons(sender, seriesId, browseType):
    """
    Opens a list of Seasons for a specific TV Show

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

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
    dir = listTvShowsSeasons(dir, browseType, filter, sortorder, seriesId, 0, 200)
    if (len(dir) < 1):
        Log.Warn('Trying to access an empty tv show')
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir


def openTvShowsEpisodes(sender, seasonNum, seriesId, browseType):
    """
    Opens a TV Show Season.

    @type sender:
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

    @type seasonNum:
    @param seasonNum:

    @type seriesId: 
    @param seriesId:

    @type browseType: str
    @param browseType:

    @rtype:
    @return:
    """

    Log.Info('Opening Tv Show Episodes')
    filter = getFilterOptions()
    Log.Info('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log.Info('Sorting on %s' % sortorder)
    dir = MediaContainer(viewGroup="WallStream")
    dir = listTvShowsEpisodes(dir, browseType, filter, sortorder, seasonNum, seriesId, 0, 200)
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
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

    @type: query:
    @param query: The specific search query
    
    @rtype: 
    @return:
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = API_USER + "login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    dir = MediaContainer(viewGroup="InfoList")
    Log.Info('Listing Search Results for: %s' % query)
    URL = API_META + "search/1?offset=0&count=20&q=" + String.Quote(query)
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1
        back = "";
        if len(movie["screenshots"]) > 0:
            back = movie["screenshots"][0]["url"]
        dir.Append(
            Function(
                PopupDirectoryItem(showMoviePopup,
                    movie["originalTitle"],
                    subtitle= "Price: %s" % (movie["price"]),
                    summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                    thumb = movie["posterUrl"],
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
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

    @type videoId:
    @param videoId:

    @type trailerURL:
    @param trailerURL: 

    @type price:
    @param price:
    
    @rtype:
    @return: 
    """

    Log.Info('Showing popup menu for: %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList")
    MOVIE_URL = "http://www.voddler.com/playapi/embedded/1?videoId=" + videoId + "&session=" + Dict["sessionId"] + "&format=html&plex=1&wmode=opaque"
    if price == "Free":
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
    # add trailer
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
    # add playlists
    URL = API_USER + "playlists/1?session=" + Dict['sessionId']
    g = JSON.ObjectFromURL(URL, cacheTime=5)
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
    @param sender: Contains an ItemInfoRecord object, including information about the previous window state and the item that initiated the function call.

    @type videoId: 
    @param videoId: 

    @type playlistId:
    @param playlistId:

    @type modify:
    @param modify:

    @rtype:
    @return: A MessageContainer with return status
    """

    URL = API_USER + "playlists/1?session=" + Dict['sessionId']
    g = JSON.ObjectFromURL(URL, cacheTime=5)
    if modify == "add":
        URL = API_USER + "playlistadd/1?session=" + Dict['sessionId'] + "&playlist=" + playlistId + "&video=" + videoId
        g = JSON.ObjectFromURL(URL, cacheTime=5)
        if g['message'] != "Added" or g['success'] != True:
            Log.Error('Error, Video was not added to your playlist')
            mc = MessageContainer("Error", "Video was not added to your playlist")
        else:
            Log.Info('Video: %s was added to playlist: %s' % (videoId, playlistId))
            mc = MessageContainer("Success", "Video added to playlist") 
    elif modify == "del":
        URL = API_USER + "playlistremove/1?session=" + Dict['sessionId'] + "&playlist=" + playlistId + "&video=" + videoId
        g = JSON.ObjectFromURL(URL, cacheTime=5)
        if g['message'] != "Removed" or g['success'] != True:
            Log.Error('Error, Video was not removed from your playlist')
            mc = MessageContainer("Error", "Video was not removed from your playlist")
        else:
            Log.Info('Video: %s was added to playlist: %s' % (videoId, playlistId))
            mc = MessageContainer("Success", "Video was removed from your playlist") 
    else:
         Log.Error('Error, Unkown modify tag')
         mc = MessageContainer("Error", "Unknown modify tag")
    return mc 


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

