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

    ###################
    ####  AUTEURS  ####
    ###################
    
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
                    "image": item["img"]["value"]
                })

        return authors
    
    # Gets all mangaka authors
    def get_author_detail(self, name):

        name = name.replace("_", " ").replace("%2F", "/")

        q = """
            SELECT distinct ?name ?img ?nationality ?comment ?website ?birthdate ?birthplace
            WHERE {
                ?manga dbo:type dbr:Manga .
                ?manga dbo:author ?author .
                OPTIONAL {
                    ?author dbo:thumbnail ?img .
                    ?author foaf:name ?name .
                    ?author dbp:nationality ?nationality .
                    ?author rdfs:comment ?comment .
                    ?author dbp:website ?website .
                    ?author dbp:birthDate ?birthdate .
                    ?author dbp:birthPlace ?birthplace .
                    FILTER regex(?name, """ + "\"" + name + "\"" + """) .
                    FILTER langMatches(lang(?comment), 'fr')
                }
            }
        """

        results = self.get_results(q)
        author = {}

        print(results)

        for item in results:
            date = ""
            if "birthdate" in item:
                date = item["birthdate"]["value"].split("-")
                date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
                date = date.strftime("%d %b %Y")

            author = {
                "label": item["name"]["value"].replace("/", "%2F") if "name" in item else name,
                "image": item["img"]["value"] if "img" in item else False,
                "nationality": item["nationality"]["value"] if "nationality" in item else False,
                "comment": item["comment"]["value"] if "comment" in item else "Pas de presentation disponible",
                "website": item["website"]["value"] if "website" in item else "Pas de site disponible",
                "birthdate": date if "date" != item else "Pas de date disponible",
                "birthplace": item["birthplace"]["value"] if "birthplace" in item else "Pas de ville disponible",
            }

        return author
    

    ###################
    ####   MANGAS  ####
    ###################
    
    def get_all_mangas_count(self):
        q = """
            SELECT DISTINCT count(*) AS ?nb_mangas
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbo:thumbnail ?image.
                ?x dbp:name ?mangaLabel.
            }
        """

        return self.get_results(q)[0]["nb_mangas"]["value"]

    def get_all_mangas(self, page, offset):
        limit = str(offset)
        offset = "0" if int(page) == 1 else str((int(page)-1)*int(limit))
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbo:thumbnail ?image.
                ?x dbp:name ?mangaLabel.
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
                "image": item["image"]["value"].replace('http://commons.wikimedia.org/wiki/Special:FilePath/', 'https://en.wikipedia.org/wiki/Special:FilePath/')
            })

        return mangas

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