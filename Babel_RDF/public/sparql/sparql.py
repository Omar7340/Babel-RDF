# make a request on sparql endpoint on dbpedia
from distutils.command.build import build
import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

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
    
    # Gets all mangaka authors
    def get_all_authors(self):

        q = """
            SELECT distinct ?name ?img
            WHERE {
                ?manga dbo:type dbr:Manga .
                ?manga dbo:author ?author .
                ?author dbo:thumbnail ?img .
                ?author dbp:name ?name
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
    def get_author_detail(self, label):

        q = """
            SELECT distinct ?name ?img
            WHERE {
                ?manga dbo:type dbr:Manga .
                ?manga dbo:author ?author .
                ?author dbo:thumbnail ?img .
                ?author dbp:name ?name
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
    
    def get_all_mangas(self):
        q = """
            SELECT ?manga ?mangaLabel WHERE {
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                ?manga wdt:P31 wd:Q8274.
            }
        """

        return self.get_results(q)

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