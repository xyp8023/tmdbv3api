# https://github.com/xyp8023/tmdbv3api
# import numpy as np
# import time
import json
# import pandas as pd
# import os
import csv
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

        self.language_dict = {}
        # build the language database (ISO 639-1)
        with open('./csv/language-codes_csv.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.language_dict[row[1]]=row[0]

        self.person = Person(self.tmdb)
        self.company = Company(self.tmdb)
    
    def set_language(self, language):
        # language:  English, Spanish, etc
        self.tmdb.language = self.language_dict[language]

    def search_movies(self, genre=None, without_genre=None, cast=None, crew=None, people=None, company=None, year=None, upper_year=None, lower_year=None, rating=None, language=None, top=10):
        """
        with_genres: string: Comma separated value of genre ids that you want to include in the results.
        without_genres: string: Comma separated value of genre ids that you want to exclude from the results.
        with_cast: string: A comma separated list of person ID's. Only include movies that have one of the ID's added as an actor.
        with_crew: string: A comma separated list of person ID's. Only include movies that have one of the ID's added as a crew member.
        with_people: string: A comma separated list of person ID's. Only include movies that have one of the ID's added as a either a actor or a crew member.
        with_companies: string: A comma separated list of production company ID's. Only include movies that have one of the ID's added as a production company.
        year: integer: A filter to limit the results to a specific year (looking at all release dates).
        release_date.gte: string (year-month-day): Filter and only include movies that have a release date (looking at all release dates) that is greater or equal to the specified value.
        release_date.lte: string (year-month-day): Filter and only include movies that have a release date (looking at all release dates) that is less than or equal to the specified value.
        vote_average.gte: number: Filter and only include movies that have a rating that is greater or equal to the specified value.
        with_original_language: string: Specify an ISO 639-1 string to filter results by their original language value.
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
        else:
            if upper_year is not None:
                request_dic['release_date.lte'] = str(upper_year)+"-12-31"
            if lower_year is not None:
                request_dic['release_date.gte'] = str(lower_year)+"-01-01"

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
        
        if language is not None:
            request_dic['with_original_language'] = self.language_dict[language]
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


    # search by genre, upper year
    show = tmdb_base.search_movies(genre="Romance", upper_year=2010)
    print(show, '\n')

    # search by genre, lower year
    show = tmdb_base.search_movies(genre="Romance", lower_year=2010)
    print(show, '\n')

    # search by genre, original language
    show = tmdb_base.search_movies(genre="Romance",language="Swedish")
    print(show, '\n')