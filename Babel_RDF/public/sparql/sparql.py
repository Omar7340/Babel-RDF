# make a request on sparql endpoint on dbpedia
import requests

class Sparql:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        # self.prefix = {
        #     "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        #     "dbp":"http://dbpedia.org/property/",
        #     "dbo":"http://dbpedia.org/ontology/",
        #     "xsd":"http://www.w3.org/2001/XMLSchema#"
        #     }

        self.prefix = {
            "wd" : "http://www.wikidata.org/entity/",
            "wdt" : "http://www.wikidata.org/prop/direct/",
            "wikibase" : "http://wikiba.se/ontology#",
            "p" : "http://www.wikidata.org/prop/",
            "ps" : "http://www.wikidata.org/prop/statement/",
            "pq" : "http://www.wikidata.org/prop/qualifier/",
            "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
            "bd" : "http://www.bigdata.com/rdf#"
        }

    def get_prefixes(self):
        result = ""
        for k, v in self.prefix.items():
            result += "PREFIX {k}: <{v}>\n".format(k=k, v=v)
        
        return result

    def query(self, q):
        try:
            query = self.get_prefixes() + q
            params = {'query': query}
            resp = requests.get(self.endpoint, params=params, headers={'Accept': 'application/sparql-results+json'})
            return resp.text
        except Exception as e:
            print(e, file=sys.stdout)
            raise
    
    def get_all_mangas(self):
        q = """
            SELECT ?manga ?mangaLabel WHERE {
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                ?manga wdt:P31 wd:Q8274.
            }
        """

        return self.query(q)

# Exemple
# q1 = """
#     select DISTINCT  ?u where {
#               ?s rdf:type dbo:BasketballPlayer .
#                 ?s dbo:team ?team .
#                 ?team foaf:name ?u
#     } LIMIT 10
# """
# spqr = Sparql("https://query.wikidata.org/sparql")
# print(sparql.get_all_mangas())