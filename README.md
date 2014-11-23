email_crawler
=============

Mon premier crawler utilisant scrapy

Pour commencer à crawler:
```shell
$ pip install -r requirements.txt
$ export CHRIS_LOGIN=votre-login
$ export CHRIS_PASSWORD=votre-mot-de-passe
$ scrapy crawl chris -o email.json
```

Cela créera un fichier email.json contenant les emails.

Il crawle toutes les adresses email à partir du mot-clé 'finance'. Pour changer de mot-clé, il suffit de changer la ligne:
```python
factory = FormDataFactory(rows=250, keyword='finance')
```

du fichier chris/spiders/chris_spider.py
