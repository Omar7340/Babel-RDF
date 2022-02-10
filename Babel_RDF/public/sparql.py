# make a request on sparql endpoint on dbpedia
import requests

class Sparql:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.default_graph_uri = "http://dbpedia.org"
        self.prefix = {
            "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dbp":"http://dbpedia.org/property/",
            "dbo":"http://dbpedia.org/ontology/",
            "xsd":"http://www.w3.org/2001/XMLSchema#"
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
            resp = requests.get(self.endpoint, params=params, headers={'Accept': 'application/json'})
            return resp.text
        except Exception as e:
            print(e, file=sys.stdout)
            raise

# Exemple
# q1 = """
#     select DISTINCT  ?u where {
#               ?s rdf:type dbo:BasketballPlayer .
#                 ?s dbo:team ?team .
#                 ?team foaf:name ?u
#     } LIMIT 10
# """
# sparql = Sparql("http://dbpedia.org/sparql")
# print(sparql.query(q1))