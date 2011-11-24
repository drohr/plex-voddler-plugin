# -*- encoding: utf-8
#
# Voddler Plex Plugin
#

import re

VERSION="0.2"
VIDEO_PREFIX = "/video/voddler"
NAME = L('Title')
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

####################################################################################################


def ValidatePrefs():
    u = Prefs['username']
    p = Prefs['password']
    f = Prefs['filter']
    if( u == None or p == None or f == None):
        return MessageContainer(
            "Error",
            "You need to provide a username and password to use this service"
        )

def Start():
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
                subtitle="Movies",
                summary="",
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
                subtitle="TV Shows",
                summary="",
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
                subtitle="Documentaries",
                summary="",
                thumb=R('plex_icon_docus.png'),
                art=R(ART)
            ), genreCategory = "documentary", browseType = "documentary"
        )
    )
    # preference tab
    dir.Append(
        PrefsItem(
            title="Preferences",
            subtitle="Set up Voddler access details",
            summary="Make sure the Voddler Tray app is running in the background.",
            thumb=R('plex_icon_settings.png'),
            art=R(ART)
        )
    )
    return dir

def ListMovieGenres(sender, genreCategory, browseType):
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

def ListTvShowsSeasons(dir, browseType, category, sort, seriesId, offset, count):
    dir = MediaContainer(viewGroup="InfoList")
    URL = "https://api.voddler.com/metaapi/seriesinfo/1?seriesId=" + seriesId
    j = JSON.ObjectFromURL(URL)
    i = 0
    seasons = {}
    for seasonNum, season in j["data"]["seasons"].items():
        seasonNum = int(seasonNum)
        season["num"] = seasonNum
        seasons[seasonNum] = season
    
    for season in seasons.values():
        i = i + 1
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
    URL = "https://api.voddler.com/metaapi/browse/1?type=%s&category=%s&sort=%s&offset=%d&count=%d&genre=%s" % (browseType, category, String.Quote(sort, usePlus=False), offset, count, String.Quote(genre, usePlus=False))
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1
        back = "";
        if len(movie["screenshots"]) > 0:
            back = movie["screenshots"][0]["url"]
        MOVIE_URL = "http://www.voddler.com/playapi/embedded/1?videoId=" + movie["id"] + "&session=" + Dict["sessionId"] + "&format=html&wmode=opaque"
        dir.Append(
            WebVideoItem(MOVIE_URL,
                title= movie["originalTitle"],
                subtitle= "Price: %s" % (movie["price"]),
                summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                thumb = movie["posterUrl"],
                duration = movie["runtime"],
                userRating=float(movie['videoRatingAverage']) / 5 * 10,
                art=back
            )
        )
    if (i == count):
        offset = offset + count
        dir = ListMoviesInGenre(dir, browseType, category, sort, genre, offset, count)
    return dir

def ListTvShowsInGenre(dir, browseType, category, sort, genre, offset, count):
    URL = "https://api.voddler.com/metaapi/browse/1?type=" + browseType + "&category=" + Prefs['filter'] + "&sort=" + Prefs['sortorder'] + "&offset=0&count=200&genre=" + genre
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1
        dir.Append(
            Function(
                DirectoryItem(OpenTvShowsSeasons,
                    title= movie["originalTitle"],
                    subtitle= "",
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
    dir = MediaContainer(viewGroup="InfoList")
    URL = "https://api.voddler.com/metaapi/seriesinfo/1?seriesId=" + seriesId
    j = JSON.ObjectFromURL(URL)
    i = 0
    episodes = {}
    for episodeNum, episode in j["data"]["seasons"][str(seasonNum)].items():
        episodeNum = int(episodeNum)
        episode["num"] = episodeNum
        episodes[episodeNum] = episode
    
    for episode in episodes.values():
        i = i + 1
        MOVIE_URL = "http://www.voddler.com/playapi/embedded/1?videoId=" + episode["id"] + "&session=" + Dict["sessionId"] + "&format=html&wmode=opaque"
        dir.Append(
            WebVideoItem(MOVIE_URL,
                #title= episode["originalTitle"],
                title="%d. %s" % (episode["num"], episode["originalTitle"]),
                subtitle= "", #Price: %s" % (movie["price"]),
                summary = "", #Production year: %s\n\n%s" % (episode["productionYear"], removeHtmlTags(episode["localizedData"]["synopsis"])),
                thumb = episode["posterUrl"],
                duration = episode["runtime"],
                userRating=float(episode['videoRatingAverage']) / 5 * 10
            )
        )
    return dir

def OpenMovieGenre(sender, genre, browseType):
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListMoviesInGenre(dir, browseType, Prefs['filter'], Prefs['sortorder'], genre, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir

def OpenTvShowsGenre(sender, genre, browseType):
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListTvShowsInGenre(dir, browseType, Prefs['filter'], Prefs['sortorder'], genre, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir
def OpenTvShowsSeasons(sender, seriesId, browseType):
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListTvShowsSeasons(dir, browseType, Prefs['filter'], Prefs['sortorder'], seriesId, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir
def OpenTvShowsEpisodes(sender, seasonNum, seriesId, browseType):
    dir = MediaContainer(viewGroup="WallStream")
    dir = ListTvShowsEpisodes(dir, browseType, Prefs['filter'], Prefs['sortorder'], seasonNum, seriesId, 0, 200)
    if (len(dir) < 1):
        return MessageContainer(
            "Sorry",
            "Not available"
        )
    return dir

def SearchResults(sender,query=None):
    if ValidatePrefs() != None:
        return ValidatePrefs()
    dir = MediaContainer(viewGroup="InfoList")
    URL = "https://api.voddler.com/metaapi/search/1?offset=0&count=20&q=" + String.Quote(query)
    j = JSON.ObjectFromURL(URL)
    i = 0
    for movie in j["data"]["videos"]:
        i = i + 1;
        MOVIE_URL = "http://www.voddler.com/playapi/embedded/1?videoId=" + movie["id"] + "&session=" + Dict["sessionId"] + "&format=html&wmode=opaque"
        dir.Append(
            WebVideoItem(MOVIE_URL,
                title= movie["originalTitle"],
                subtitle= "Price: %s" % (movie["price"]),
                summary = "Production year: %s\n\n%s" % (movie["productionYear"], removeHtmlTags(movie["localizedData"]["synopsis"])),
                thumb = movie["posterUrl"],
                duration = movie["runtime"],
                userRating=float(movie['videoRatingAverage']) / 5 * 10
            )
        )
    if (i == 0):
        return MessageContainer(
            "Search results",
            "Did not find any result for '%s'" % query
        )
    return dir

def removeHtmlTags(text):
    p = re.compile(r'<[^<]*?/?>')
    text = p.sub('', text)
    text = text.replace("\r","")
    text = text.replace("\n","")
    text = text.replace("&amp;","")
    text = text.replace("nbsp;","")
    p = re.compile(r'(?<=[a-z])[\r\n]+')
    text = p.sub('', text)
    return text

