# websearch
Some simple web scraping to do Wikipedia and Google searches

Module de recherche Web
=======================

Exemple d'utilisation
---------------------

```
mysearch = GoogleSearch().search('test', count=2)
for result in mysearch:
	print result.url

mysearch = WikipediaSearch(base="fr.wikipedia.org").search('test', count=100)
for result in mysearch:
    print result.url, result.title
```

