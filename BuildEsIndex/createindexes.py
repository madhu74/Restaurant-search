from elasticsearch import Elasticsearch
from json import loads
ES_HOST = {"host" : "", "port" : 9200}
INDEX_NAME = 'project'
TYPE_NAME = 'restaurant'
ID_FIELD = '_id'

# create ES client, create index
es = Elasticsearch(hosts = [ES_HOST])
# es.index(index='project', doc_type='people', id=i, body=json.loads(r.content))

fh = open("elastic_content.json")
i=0
for item in fh:
    my_dict=loads(item)
    val = my_dict["_id"]["$oid"]
    del my_dict["_id"]
    my_dict["mongo_reference"] = val
    es.index(index=INDEX_NAME, doc_type=TYPE_NAME, id=i, body=my_dict)
    i=i+1
    # break
# if es.indices.exists(INDEX_NAME):
#     print("deleting '%s' index..." % (INDEX_NAME))
#     res = es.indices.delete(index = INDEX_NAME)

# print(es.get(index=INDEX_NAME, doc_type=TYPE_NAME, id='1'))
