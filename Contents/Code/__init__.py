# -*- encoding: utf-8
#
# Voddler Plex Plugin
#

import re

VERSION="2.5"
VIDEO_PREFIX = "/video/voddler"
NAME = L('Title')
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

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
    Log('Voddler Plugin initialized')


def ShowTypes():
    """
    Shows the start menu.

    """
    
    Log('Showing Default Menu options')
    dir = MediaContainer(viewGroup="InfoList")
    # search
    dir.Append(
        Function(
            InputDirectoryItem(SearchResults,
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
            DirectoryItem(ListMovieGenres,
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
            DirectoryItem(ListTvShowGenres,
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
            DirectoryItem(ListMovieGenres,
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
            DirectoryItem(ListFavorites,
                "Favorites",
                subtitle="",
                summary="List of all your favorite movies",
                thumb=R('plex_icon_favorites.png'),
                art=R(ART)
            )
        )
    )
    # list playlist
    dir.Append(
         Function(
            DirectoryItem(ListPlaylist,
                "Playlist",
                subtitle="",
                summary="List of all movies in your current playlist",
                thumb=R('plex_icon_playlist.png'),
                art=R(ART)
            )
        )
    )
    # list history
    dir.Append(
         Function(
            DirectoryItem(ListHistory,
                "History",
                subtitle="",
                summary="All the Voddler movies and episodes you have watched",
                thumb=R('plex_icon_history.png'),
                art=R(ART)
            )
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


def ListMovieGenres(sender, genreCategory, browseType):
    """
    Returning a list of movie genres.

    @param sender:
    @param genreCategory:
    @param browseType:
    """

    Log('Listing Movie Genres')

    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = "https://api.voddler.com/userapi/login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    dir = MediaContainer(viewGroup="InfoList")
    # add search to list
    dir.Append(
        Function(
            InputDirectoryItem(SearchResults,
                "Search",
                "Search",
                summary="Search for films, actors, directors, writers and more",
                thumb=R('plex_icon_search.png'),
                art=R(ART)
            )
        )
    )
    URL = "https://api.voddler.com/metaapi/genres/1?type=" + genreCategory
    g = JSON.ObjectFromURL(URL)
    for genre in g['data']:
        # show adult genre or not
        if Prefs['adultfilter'] == False:
            if genre["value"] == "explicit":
                continue
        dir.Append(
            Function(
                DirectoryItem(OpenMovieGenre,
                    genre['name'],
                    subtitle="",
                    summary="",
                    thumb=R(ICON),
                    art=R(ART)
                ), genre = genre['value'], browseType=browseType
            )
        )
    return dir


def ListTvShowGenres(sender, genreCategory, browseType):
    """
    Returning a list of TV Show genres

    @param sender:
    @param genreCategory:
    @param browseType:
    """

    Log('Listing TV Shows genres')
    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = "https://api.voddler.com/userapi/login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    dir = MediaContainer(viewGroup="InfoList")
    # add search to list
    dir.Append(
        Function(
            InputDirectoryItem(SearchResults,
                "Search",
                "Search",
                summary="Search for films, actors, directors, writers and more",
                thumb=R('plex_icon_search.png'),
                art=R(ART)
            )
        )
    )
    URL = "https://api.voddler.com/metaapi/genres/1?type=" + genreCategory
    g = JSON.ObjectFromURL(URL)
    for genre in g['data']:
        # show adult genre or not
        if Prefs['adultfilter'] == False:
            if genre["value"] == "explicit":
                continue
        dir.Append(
            Function(
                DirectoryItem(OpenTvShowsGenre,
                    genre['name'],
                    subtitle="",
                    summary="",
                    thumb=R(ICON),
                    art=R(ART)
                ), genre = genre['value'], browseType=browseType
            )
        )
    return dir


def ListFavorites(sender):
    """
    Returning a list of movies from your playlist: favorites

    @param sender:
    """
    
    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = "https://api.voddler.com/userapi/login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    Log('Listing Favorites')
    dir = MediaContainer(viewGroup="WallStream")
    URL = "https://api.voddler.com/userapi/playlists/1?session=" + Dict['sessionId']
    g = JSON.ObjectFromURL(URL)
    # get all playlists from user
    for p in g["data"]["playlists"]:
        # get all videos for a specific playlist
        if p["type"] == "favorites":
            for v in p["videos"]:
                # get all information for specific video
                URLinfo = "https://api.voddler.com/metaapi/info/1?videoId=" + v['id']
                j = JSON.ObjectFromURL(URLinfo)
                movie=j['data']['videos']
                back = "";
                if len(movie["screenshots"]) > 0:
                    back = movie["screenshots"][0]["url"]
                dir.Append(
                    Function(
                        PopupDirectoryItem(ShowMoviePopup,
                            movie["originalTitle"],
                            subtitle= "Price: %s" % (movie["price"]),
                            summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                            thumb = movie["posterUrl"],
                            duration =  movie["runtime"],
                            userRating=float(movie['videoRatingAverage']) / 5 * 10,
                            art=back
                        ), videoId = movie['id'], trailerURL = movie['trailer']
                    )
                )    
    return dir


def ListPlaylist(sender):
    """
    Returning a list of movies from your playlist: playlist

    @param sender:
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = "https://api.voddler.com/userapi/login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    Log('Listing Playlist')
    dir = MediaContainer(viewGroup="WallStream")
    URL = "https://api.voddler.com/userapi/playlists/1?session=" + Dict['sessionId']
    g = JSON.ObjectFromURL(URL)
    for p in g["data"]["playlists"]:
        if p["type"] == "playlist":
            for v in p["videos"]:
                # get all information for specific video
                URLinfo = "https://api.voddler.com/metaapi/info/1?videoId=" + v['id']
                j = JSON.ObjectFromURL(URLinfo)
                movie=j['data']['videos']
                back = "";
                if len(movie["screenshots"]) > 0:
                    back = movie["screenshots"][0]["url"]
                    dir.Append(
                    Function(
                        PopupDirectoryItem(ShowMoviePopup,
                            movie["originalTitle"],
                            subtitle= "Price: %s" % (movie["price"]),
                            summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                            thumb = movie["posterUrl"],
                            duration =  movie["runtime"],
                            userRating=float(movie['videoRatingAverage']) / 5 * 10,
                            art=back
                        ), videoId = movie['id'], trailerURL = movie['trailer']
                    )
                )    
    return dir


def ListHistory(sender):
    """
    Returning a list of movies from your playlist: history

    @param sender:
    """

    if ValidatePrefs() != None:
        return ValidatePrefs()
    if Prefs['username'] != None:
        URL = "https://api.voddler.com/userapi/login/1?username=" + Prefs['username'] + "&password=" + Prefs['password']
        g = JSON.ObjectFromURL(URL, cacheTime=300)
        if g['message'] != 'Welcome':
            return MessageContainer("Failed to log in", "Username or password is incorrect")
        Dict['sessionId'] = g['data']['session']

    Log('Listing History')
    dir = MediaContainer(viewGroup="WallStream")
    URL = "https://api.voddler.com/userapi/playlists/1?session=" + Dict['sessionId']
    g = JSON.ObjectFromURL(URL)
    for p in g["data"]["playlists"]:
        if p["type"] == "history":
            for v in p["videos"]:
                # get all information for specific video
                URLinfo = "https://api.voddler.com/metaapi/info/1?videoId=" + v['id']
                j = JSON.ObjectFromURL(URLinfo)
                movie=j['data']['videos']
                back = "";
                if len(movie["screenshots"]) > 0:
                    back = movie["screenshots"][0]["url"]
                    dir.Append(
                    Function(
                        PopupDirectoryItem(ShowMoviePopup,
                            movie["originalTitle"],
                            subtitle= "Price: %s" % (movie["price"]),
                            summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                            thumb = movie["posterUrl"],
                            duration =  movie["runtime"],
                            userRating=float(movie['videoRatingAverage']) / 5 * 10,
                            art=back
                        ), videoId = movie['id'], trailerURL = movie['trailer']
                    )
                )    
    return dir


def ListTvShowsSeasons(dir, browseType, category, sort, seriesId, offset, count):
    """
    Returning a list of TV Show seasons based on seriesId

    @param dir:
    @param browseType:
    @param category:
    @param sort:
    @param seriesId:
    @param offset:
    @param count:
    """

    Log('Listing TV Show seasons for: %s' % seriesId)
    dir = MediaContainer(viewGroup="InfoList")
    URL = "https://api.voddler.com/metaapi/seriesinfo/1?seriesId=" + seriesId
    j = JSON.ObjectFromURL(URL)
    seasons = {}
    for seasonNum, season in j["data"]["seasons"].items():
        seasonNum = int(seasonNum)
        season["num"] = seasonNum
        seasons[seasonNum] = season
    
    for season in seasons.values():
        dir.Append(
            Function(
                DirectoryItem(OpenTvShowsEpisodes,
                    "Season %d" % season["num"],
                    subtitle= "", 
                    summary = "", #
                    thumb = R(ICON),
                    art=R(ART)
                ), seasonNum = season["num"], seriesId=seriesId, browseType=browseType
            )
        )
    return dir


def ListMoviesInGenre(dir, browseType, category, sort, genre, offset, count):
    """
    Returning a list of Movies based on genre

    @param dir:
    @param browseType:
    @param category:
    @param sort:
    @param genre:
    @param offset:
    @param count:
    """

    Log('Listing Movies in genre: %s' % genre)
    URL = "https://api.voddler.com/metaapi/browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1
        back = "";
        if len(movie["screenshots"]) > 0:
            back = movie["screenshots"][0]["url"]
        dir.Append(
            Function(
                PopupDirectoryItem(ShowMoviePopup,
                    movie["originalTitle"],
                    subtitle= "Price: %s" % (movie["price"]),
                    summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                    thumb = movie["posterUrl"],
                    duration =  movie["runtime"],
                    userRating=float(movie['videoRatingAverage']) / 5 * 10
                ), videoId = movie['id'], trailerURL = movie['trailer']
            )
        )
    if (i == count):
        offset = offset + count
        dir = ListMoviesInGenre(dir, browseType, category, sort, genre, offset, count)
    return dir


def ListTvShowsInGenre(dir, browseType, category, sort, genre, offset, count):
    """
    Returning a list of TV Shows based on genre

    @param dir:
    @param browseType:
    @param category:
    @param sort:
    @param genre:
    @param offset:
    @param count:
    """

    Log('Listing TV Shows in genre: %s' % genre)
    URL = "https://api.voddler.com/metaapi/browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1
        dir.Append(
            Function(
                DirectoryItem(OpenTvShowsSeasons,
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
        dir = ListTvShowsInGenre(dir, browseType, category, sort, genre, offset, count)    
    return dir


def ListTvShowsEpisodes(dir, browseType, category, sort, seasonNum, seriesId, offset, count):
    """
    Returning a list of TV Shows episodes based on seriesId and seasonNum

    @param dir:
    @param browseType:
    @param category:
    @param sort:
    @param seasonNum:
    @param seriesId:
    @param offset:
    @param count:
    """

    Log('Listing TV Show episodes for %s' % seriesId)
    dir = MediaContainer(viewGroup="InfoList")
    URL = "https://api.voddler.com/metaapi/seriesinfo/1?seriesId=" + seriesId
    j = JSON.ObjectFromURL(URL)
    episodes = {}
    for episodeNum, episode in j["data"]["seasons"][str(seasonNum)].items():
        episodeNum = int(episodeNum)
        episode["num"] = episodeNum
        episodes[episodeNum] = episode
    
    for episode in episodes.values():
        URLinfo = "https://api.voddler.com/metaapi/info/1?videoId=" +  episode["id"]
        j = JSON.ObjectFromURL(URLinfo)
        movie=j['data']['videos']
        # Set correct episode title
        if episode["originalTitle"] == "" or episode["originalTitle"] == "null":
            originalTitle = movie["originalTitle"]
        else:
            originalTitle = episode["originalTitle"]
        dir.Append(
            Function(
                PopupDirectoryItem(ShowMoviePopup,
                    title="%d. %s" % (episode["num"], originalTitle),
                    subtitle= "Price: %s" % (movie["price"]),
                    summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                    thumb = "",
                    duration =  movie["runtime"],
                    userRating=float(movie['videoRatingAverage']) / 5 * 10
                ), videoId = movie['id'], trailerURL = movie['trailer']
            )
        )
    return dir


def OpenMovieGenre(sender, genre, browseType):
    """
    Opens a Movie genre.

    @param sender:
    @param genre: 
    @param browseType:
    """

    Log('Opening Movie Genres')
    filter = getFilterOptions()
    Log('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log('Sorting on %s' % sortorder)
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListMoviesInGenre(dir, browseType, filter, sortorder, genre, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir


def OpenTvShowsGenre(sender, genre, browseType):
    """
    Opens a TV Show genre.

    @param sender:
    @param genre:
    @param browseType:
    """

    Log('Opening Tv Show Genres')
    filter = getFilterOptions()
    Log('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log('Sorting on %s' % sortorder)
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListTvShowsInGenre(dir, browseType, filter, sortorder, genre, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir


def OpenTvShowsSeasons(sender, seriesId, browseType):
    """
    Opens a list of Seasons for a specific TV Show

    @param sender:
    @param seriesId:
    @param broweType:
    """

    Log('Opening Tv Show Seasons')
    filter = getFilterOptions()   
    Log('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log('Sorting on %s' % sortorder)
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListTvShowsSeasons(dir, browseType, filter, sortorder, seriesId, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir


def OpenTvShowsEpisodes(sender, seasonNum, seriesId, browseType):
    """
    Opens a TV Show Season.

    @param sender:
    @param seasonNum:
    @param seriesId:
    @param browseType:
    """

    Log('Opening Tv Show Episodes')
    filter = getFilterOptions()
    Log('Filtering on %s' % filter)
    sortorder = getSortOptions()
    Log('Sorting on %s' % sortorder)
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListTvShowsEpisodes(dir, browseType, filter, sortorder, seasonNum, seriesId, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir


def SearchResults(sender,query=None):
    """
    Displays output from a search.

    @param sender:
    @param query: The specific search query
    """

    Log('Displaying Search Results')
    if ValidatePrefs() != None:
        return ValidatePrefs()
    dir = MediaContainer(viewGroup="InfoList")
    URL = "https://api.voddler.com/metaapi/search/1?offset=0&count=20&q=" + String.Quote(query)
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1
        back = "";
        if len(movie["screenshots"]) > 0:
            back = movie["screenshots"][0]["url"]
        dir.Append(
            Function(
                PopupDirectoryItem(ShowMoviePopup,
                    movie["originalTitle"],
                    subtitle= "Price: %s" % (movie["price"]),
                    summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                    thumb = movie["posterUrl"],
                    duration =  movie["runtime"],
                    userRating=float(movie['videoRatingAverage']) / 5 * 10
                ), videoId = movie['id'], trailerURL = movie['trailer']
            )
        )
    if (i == 0):
        return MessageContainer(
            "Search results",
            "Did not find any result for '%s'" % query
        )
    return dir


def ShowMoviePopup(sender, videoId, trailerURL):
    """
    Show popup menu for a movie.

    @param sender:
    @param videoId:
    @param trailerURL: 
    """

    Log('Showing popup menu for %s' % videoId)
    dir = MediaContainer(viewGroup="InfoList")
    MOVIE_URL = "http://www.voddler.com/playapi/embedded/1?videoId=" + videoId + "&session=" + Dict["sessionId"] + "&format=html&lab=1&wmode=opaque&plex=1"
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
    # WIP
    #dir.Append(
    #    WebVideoItem(MOVIE_URL,
    #        title= "Add to Favorites",
    #        subtitle="",
    #        summary="",
    #        thumb="",
    #        duration= "",
    #        userRating="",
    #        art=""
    #    )
    #)
    #dir.Append(
    #    WebVideoItem(MOVIE_URL,
    #        title= "Add to Playlist",
    #        subtitle="",
    #        summary="",
    #        thumb="",
    #        duration= "",
    #        userRating="",
    #        art=""
    #    )
    #)
    #
    return dir


def removeHtmlTags(text):
    """
    Removes wierd tags from synopsis text.

    @param text: synopsis from videoId.
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

