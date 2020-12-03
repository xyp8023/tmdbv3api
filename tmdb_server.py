# https://github.com/xyp8023/tmdbv3api
# import numpy as np
# import time
import json
# import pandas as pd
# import os
from tmdbv3api import TMDb, Movie, Discover, Genre, Person, Company

class tmdb_base():
    def __init__(self):
        api_key = "e9ee4dd66aa205b259f29ccb98e9a989"
        self.tmdb = TMDb()
        self.tmdb.api_key = api_key
        self.tmdb.language = 'en'
        self.tmdb.debug = True
        
        self.movie = Movie(self.tmdb)
        self.discover = Discover(self.tmdb)
        
        # build the genre database
        self.genre = Genre(self.tmdb)
        genres = self.genre.movie_list() # list
        self.genres_dict = {} # a dict with keys: genre names and values: id
        for g in genres:
            self.genres_dict[g.name] = g.id
        # the available genre:
        # {'Action': 28, 'Adventure': 12, 'Animation': 16, 'Comedy': 35, 
        # 'Crime': 80, 'Documentary': 99, 'Drama': 18, 'Family': 10751, 
        # 'Fantasy': 14, 'History': 36, 'Horror': 27, 'Music': 10402, 
        # 'Mystery': 9648, 'Romance': 10749, 'Science Fiction': 878, 
        # 'TV Movie': 10770, 'Thriller': 53, 'War': 10752, 'Western': 37}

        self.person = Person(self.tmdb)
        self.company = Company(self.tmdb)
        
    def search_movies(self, genre=None, without_genre=None, cast=None, crew=None, people=None, company=None, year=None, rating=None, top=10):
        """
        with_genres: string: Comma separated value of genre ids that you want to include in the results.
        without_genres: string: Comma separated value of genre ids that you want to exclude from the results.
        with_cast: string: A comma separated list of person ID's. Only include movies that have one of the ID's added as an actor.
        with_crew: string: A comma separated list of person ID's. Only include movies that have one of the ID's added as a crew member.
        with_people: string: A comma separated list of person ID's. Only include movies that have one of the ID's added as a either a actor or a crew member.
        with_companies: string: A comma separated list of production company ID's. Only include movies that have one of the ID's added as a production company.
        year: integer: A filter to limit the results to a specific year (looking at all release dates).
        vote_average.gte: number: Filter and only include movies that have a rating that is greater or equal to the specified value.
        """

        request_dic = {}
        request_dic['sort_by'] = 'vote_average.desc'
        request_dic['vote_count.gte']=10

        if genre is not None:
            request_dic['with_genres'] = str(self.genres_dict[genre])
        if without_genre is not None:
            request_dic['without_genres'] = str(self.genres_dict[without_genre])
        if year is not None:
            request_dic['year']=year
        if rating is not None:
            request_dic['vote_average.gte'] = rating
        if company is not None:
            company_id = self.company.search_id(company)
            if len(company_id)>0:
                # sort company_id because there might be many of them
                company_id = [item.id for item in company_id]
                request_dic['with_companies'] =  str(sorted(company_id)[0])

        # if len(person_id)==0, it means we don't have the person in the database
        # we simply just ignore that person
        if cast is not None:
            person_id = self.person.search_id(cast)
            if len(person_id)>0:
                request_dic['with_cast'] = str(person_id[0])            
        elif crew is not None:
            person_id = self.person.search_id(crew)
            if len(person_id)>0:
                request_dic['with_crew'] = str(person_id[0])
        elif people is not None:
            person_id = self.person.search_id(people)
            if len(person_id)>0:
                request_dic['with_people'] = str(person_id[0])
           
        show = self.discover.discover_movies(request_dic)

        # return the top 5 list by default
        return str(show[:top])


if __name__ == "__main__":
    tmdb_base = tmdb_base()

    # example: 
    # {"actors": {"selected": ["Johnny Depp"],"deselected": ["Will Smith"]},"genres": {"selected": ["romance"],"deselected": ["comedy"]},"years": {"lower": 2000,"upper": null},"rating": 2}

    # search by genre
    show = tmdb_base.search_movies(genre="Action")
    print(show, '\n')

    # search by genre, actor
    show = tmdb_base.search_movies(genre="Action", cast="Brad Pitt")
    print(show, '\n')

    # search by genre, actor, year
    show = tmdb_base.search_movies(genre="Action", cast="Will Smith", year=2010)
    print(show, '\n')

    # search by genre, year
    show = tmdb_base.search_movies(genre="Action",  year=2010)
    print(show, '\n')

    # search by genre, crew
    show = tmdb_base.search_movies(genre="Action", people="Martin Scorsese")
    print(show, '\n')

    # search by genre, without genre
    show = tmdb_base.search_movies(genre="Romance", without_genre="Comedy")
    print(show, '\n')

    # search by genre, rating
    show = tmdb_base.search_movies(genre="Romance", rating=2)
    print(show, '\n')

    # search by genre, compony
    # show = tmdb_base.search_movies(genre="Romance", company='Walt Disney Pictures')
    show = tmdb_base.search_movies(genre="Romance", company='Disney')

    print(show, '\n')