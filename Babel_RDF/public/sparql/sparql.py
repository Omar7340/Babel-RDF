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
            SELECT DISTINCT ?author ?authorLabel ?image WHERE {
                ?manga wdt:P31 wd:Q8274 .
                ?manga wdt:P50 ?author .
                ?author wdt:P18 ?image .
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """

        results = self.get_results(q)
        authors = []

        for item in results:
            authors.append({
                "id": item["author"]["value"].split("/")[-1],
                "label": item["authorLabel"]["value"],
                "image": item["image"]["value"]
            })

        return authors
    

    ###################
    ####   MANGAS  ####
    ###################
    
    # récupére le nombre de mangas
    def get_all_mangas_count(self):
        q = """
            SELECT DISTINCT count(*) AS ?nb_mangas
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                OPTIONAL {
                    ?x dbo:thumbnail ?image.
                }
            }
        """

        return self.get_results(q)[0]["nb_mangas"]["value"]

    # récupére tous les mangas (nom, image)
    def get_all_mangas(self, page, offset):
        limit = str(offset)
        offset = "0" if int(page) == 1 else str((int(page)-1)*int(limit))
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                OPTIONAL {
                    ?x dbo:thumbnail ?image.
                }
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

    def get_manga_details(self, name):
        q = """
            SELECT DISTINCT *
            WHERE {
                ?x rdf:type dbo:Manga.
                ?x dbp:name ?mangaLabel.
                OPTIONAL {
                    ?x dbo:thumbnail ?image.
                    ?x dbo:abstract ?desc.
                    ?x dbo:author ?author.
                    ?x dbp:publisher ?publisher.
                    ?x dbo:firstPublicationDate ?firstPublicationDate.
                    ?x dbp:genre ?genre.
                    ?x dbp:demographic ?demographic.
                    ?x dbp:volumes ?volumes.
                    ?x foaf:depiction ?banner.
                }
                FILTER (?mangaLabel = \""""+ name +"""\"@en)
            }
        """

        results = self.get_results(q)

        # print(results)

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
#     SELECT distinct 
#         ?url,
#         ?image
#     WHERE {
#         ?url dbo:type dbr:Manga .
#         ?x dbo:thumbnail ?image .
#     } 
# """
# spqr = Sparql()
# print(spqr.get_results(q1))