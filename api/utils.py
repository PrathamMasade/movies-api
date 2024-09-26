from collections import Counter

def extract_movies_from_collections(collections):
    movielist = []
    
    #Instead of directly taking from the database its better to iterate through the collections again.
    #This is Because some collections may be deleted but the movies may remain

    for c in collections:
        movielist.extend(c.movies.all())
    return movielist

def get_top_genres(movielist):
    genres_list = []
    for m in movielist:
        genres = m.genres.split(',')
        genres_list.extend([genre.strip() for genre in genres if genre.strip()])
    
    genre_counts = Counter(genres_list)
    return genre_counts.most_common(3)