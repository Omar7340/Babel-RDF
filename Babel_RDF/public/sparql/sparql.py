# make a request on sparql endpoint on dbpedia
from distutils.command.build import build
import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import datetime

class Sparql:
    def __init__(self, endpoint = "https://dbpedia.org/sparql"):
        self.endpoint = endpoint
        self.prefix = {
            "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dbp":"http://dbpedia.org/property/",
            "dbo":"http://dbpedia.org/ontology/",
            "dbr":"http://dbpedia.org/resource/",
            "xsd":"http://www.w3.org/2001/XMLSchema#"
        }

        # self.prefix = {
        #     "wd" : "http://www.wikidata.org/entity/",
        #     "wdt" : "http://www.wikidata.org/prop/direct/",
        #     "wikibase" : "http://wikiba.se/ontology#",
        #     "p" : "http://www.wikidata.org/prop/",
        #     "ps" : "http://www.wikidata.org/prop/statement/",
        #     "pq" : "http://www.wikidata.org/prop/qualifier/",
        #     "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
        #     "bd" : "http://www.bigdata.com/rdf#"
        # }

    def get_prefixes(self):
        result = ""
        for k, v in self.prefix.items():
            result += "PREFIX {k}: <{v}>\n".format(k=k, v=v)
        
        return result

    def build_query(self, q):
        return self.get_prefixes() + q

    def get_results(self, query):
        query = self.build_query(query)

        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(self.endpoint, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()

        result = result["results"]["bindings"]

        return result



    #################
    ####   HOME  ####
    #################

    # Get mangas for slider
    def get_slider_manga(self):
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                ?x dbo:thumbnail ?image.
                ?x dbo:firstPublicationDate ?firstPublicationDate.
                ?x dbo:lastPublicationDate ?lastPublicationDate.
                ?x dbp:genre ?genre.
                ?x dbp:demographic ?demographic.
            }
            LIMIT 4
        """

        results = self.get_results(q)

        mangas = []

        for item in results:
            mangas.append({
                "id": item["x"]["value"].split("/")[-1],
                "label": item["mangaLabel"]["value"] if "mangaLabel" in item  else 'undefined',
                "image": item["image"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/') if "image" in results[0]  else 'undefined',
                "year": item["firstPublicationDate"]["value"].split('-')[0] if "firstPublicationDate" in item  else 'undefined',
                "firstPublicationDate": item["firstPublicationDate"]["value"] if "firstPublicationDate" in item  else 'undefined',
                "lastPublicationDate": item["lastPublicationDate"]["value"] if "lastPublicationDate" in item  else 'undefined',
                "genre": [
                    item["demographic"]["value"] if "demographic" in item  else 'undefined',
                    item["genre"]["value"].split('/')[-1] if "genre" in item  else 'undefined'
                ]
            })

        return mangas

    # Get the last eight mangas publicated
    def get_last_eight_mangas_publicated(self):
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                ?x dbo:lastPublicationDate ?lastPublicationDate
                OPTIONAL { ?x dbo:thumbnail ?image. }
            }
            ORDER BY DESC(?lastPublicationDate)
            LIMIT 8
        """

        results = self.get_results(q)
        mangas = []

        for item in results:
            mangas.append({
                "id": item["x"]["value"].split("/")[-1],
                "label": item["mangaLabel"]["value"],
                "image": item["image"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/') if "image" in item  else 'undefined',
                "date": item["lastPublicationDate"]["value"] if "lastPublicationDate" in item  else 'undefined'
            })

        return mangas

    # Get the manga with the most volume
    def get_mangas_with_most_volume(self):
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                ?x dbo:numberOfVolumes ?volumes.
                OPTIONAL { ?x dbo:thumbnail ?image. }
            }
            ORDER BY DESC(?volumes)
            LIMIT 8
        """

        results = self.get_results(q)
        mangas = []

        for item in results:
            mangas.append({
                "id": item["x"]["value"].split("/")[-1],
                "label": item["mangaLabel"]["value"],
                "image": item["image"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/') if "image" in item  else 'undefined',
                "volumes": item["volumes"]["value"] if "volumes" in item  else 'undefined'
            })

        return mangas

    ####################
    ####   AUTHORS  ####
    ####################
    
    # Gets all mangaka authors
    def get_all_authors(self):

        q = """
            SELECT distinct ?name ?img
            WHERE {
                ?manga dbo:type dbr:Manga .
                ?manga dbo:author ?author .
                ?author dbo:thumbnail ?img .
                ?author foaf:name ?name
            } 
        """

        results = self.get_results(q)
        authors = []

        for item in results:
            if item["name"]["value"] != '' and item["img"]["value"]:
                authors.append({
                    "label": item["name"]["value"].replace("/", "%2F"),
                    "image": item["img"]["value"] if "img" in item.keys() else False,
                })

        return authors
    
    # Gets all mangaka authors
    def get_author_detail(self, name):

        name = name.replace("_", " ").replace("%2F", "/")

        q = """
            SELECT distinct ?name ?img ?nationality ?comment ?website ?birthdate ?birthplaceLabel
            WHERE {
                ?manga dbo:type dbr:Manga .
                ?manga dbo:author ?author .
                OPTIONAL { ?author dbo:thumbnail ?img .} .
                OPTIONAL { ?author foaf:name ?name .} .
                OPTIONAL { ?author dbp:nationality ?nationality .} .
                OPTIONAL { ?author rdfs:comment ?comment .} .
                OPTIONAL { 
                    FILTER langMatches(lang(?comment), 'en') .
                } .
                OPTIONAL { ?author dbp:website ?website .} .
                OPTIONAL { ?author dbp:birthDate ?birthdate .} .
                OPTIONAL { 
                    ?author dbp:birthPlace ?birthplace .
                    ?birthplace rdfs:label ?birthplaceLabel .
                    FILTER langMatches(lang(?birthplaceLabel), 'en') .
                } .
                FILTER regex(?name, """ + "\"" + name + "\"" + """) .
            }
        """

        item = self.get_results(q)
        item = item[0]

        date = ""
        if "birthdate" in item:
            date = item["birthdate"]["value"].split("-")
            date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
            date = date.strftime("%d %b %Y")

        author = {
            "label": item["name"]["value"].replace("/", "%2F") if "name" in item.keys() else name,
            "image": item["img"]["value"] if "img" in item.keys() else False,
            "nationality": item["nationality"]["value"] if "nationality" in item.keys() else False,
            "comment": item["comment"]["value"] if "comment" in item.keys() else "Pas de presentation disponible",
            "website": item["website"]["value"] if "website" in item.keys() else "Pas de site disponible",
            "birthdate": date if "date" != item.keys() else "Pas de date disponible",
            "birthplace": item["birthplaceLabel"]["value"] if "birthplaceLabel" in item.keys() else "Pas de ville disponible",
        }

        return author
    

    ###################
    ####   MANGAS  ####
    ###################
    
    # Get the numbers of mangas
    def get_all_mangas_count(self):
        q = """
            SELECT DISTINCT count(*) AS ?nb_mangas
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                OPTIONAL { ?x dbo:thumbnail ?image. }
            }
        """

        return self.get_results(q)[0]["nb_mangas"]["value"]

    # Gets all mangas (name, image)
    def get_all_mangas(self, page, offset):
        limit = str(offset)
        offset = "0" if int(page) == 1 else str((int(page)-1)*int(limit))
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                OPTIONAL { ?x dbo:thumbnail ?image. }
            }
            OFFSET """+ offset +""" 
            LIMIT """+ limit +"""
        """

        results = self.get_results(q)
        mangas = []

        for item in results:
            mangas.append({
                "id": item["x"]["value"].split("/")[-1],
                "label": item["mangaLabel"]["value"],
                "image": item["image"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/') if "image" in item  else 'undefined'
            })

        return mangas

    # Get details of manga
    def get_manga_details(self, name):
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                OPTIONAL { ?x dbo:thumbnail ?image. }
                OPTIONAL { ?x dbo:abstract ?desc. }
                OPTIONAL { ?x dbo:author ?author. }
                OPTIONAL { ?x dbp:publisher ?publisher. }
                OPTIONAL { ?x dbo:firstPublicationDate ?firstPublicationDate. }
                OPTIONAL { ?x dbp:genre ?genre. }
                OPTIONAL { ?x dbp:demographic ?demographic. }
                OPTIONAL { ?x dbp:volumes ?volumes. }
                OPTIONAL { ?x foaf:depiction ?banner. }
                FILTER regex(?mangaLabel, """ + "\"" + name + "\"" + """) .
            }
        """

        results = self.get_results(q)

        manga = {
            "id": name,
            "label": results[0]["mangaLabel"]["value"] if "mangaLabel" in results[0]  else name,
            "image": results[0]["image"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/') if "image" in results[0]  else 'undefined',
            "desc": results[0]["desc"]["value"] if "desc" in results[0]  else 'undefined',
            "author": results[0]["author"]["value"].split('/')[-1].replace('_', ' ') if "author" in results[0]  else 'undefined',
            "publisher": results[0]["publisher"]["value"].split('/')[-1] if "publisher" in results[0]  else 'undefined',
            "year": results[0]["firstPublicationDate"]["value"].split('-')[0] if "firstPublicationDate" in results[0]  else 'undefined',
            "firstPublicationDate": results[0]["firstPublicationDate"]["value"] if "firstPublicationDate" in results[0]  else 'undefined',
            "genre": [
                results[0]["demographic"]["value"] if "demographic" in results[0]  else 'undefined',
                results[0]["genre"]["value"].split('/')[-1] if "genre" in results[0]  else 'undefined'
            ],
            "volumes": results[0]["volumes"]["value"] if "volumes" in results[0]  else 'undefined',
            "banner": results[0]["banner"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/') if "banner" in results[0]  else 'undefined',
        }


        return manga

# Exemple
# q1 = """
#     SELECT distinct ?name ?img
#     WHERE {
#         ?manga dbo:type dbr:Manga .
#         ?manga dbo:author ?author .
#         ?author dbo:thumbnail ?img .
#         ?author dbp:name ?name
#     } 
# """
# spqr = Sparql()
# print(spqr.get_results(q1))