Welcome To Restaurants lookup application, for this application
MYSQL is used ad backend for storing the User's information.
The data set used from the application ins from the source below.

https://raw.githubusercontent.com/mongodb/docs-assets/primer-dataset/primer-dataset.json

did a CLI command

First to import in mongodb
mongoimport --db project --collection restaurants --drop --file primer-dataset.json

Later did an DB export
mongoexport --db project --collection restaurants --out elastic_content.json

this is done to have a synchronized id_ for both MongoDB and Elasticsearch
exported file later will be ingested from BuildEsIndex\createindexes.py for indexing in elasticsearch

Once the user logs-in
user can access the following link

/
/register
/login
/search/
/results/<city>/<page> ---> paginated
/restaurant/<name>
/logout
