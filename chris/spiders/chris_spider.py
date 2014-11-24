import scrapy

from chris.items import ChrisItem

import urlparse
import json
import os

class IdentifiantsManquants(Exception):
    "Exception levee quand l'utilsateur n'a pas set les variables d'env"
    pass

if 'CHRIS_LOGIN' not in os.environ or 'CHRIS_PASSWORD' not in os.environ:
    raise IdentifiantsManquants("Please set env variables CHRIS_LOGIN and CHRIS_PASSWORD")

LOGIN = os.environ['CHRIS_LOGIN']
PASSWORD = os.environ['CHRIS_PASSWORD']

class FormDataFactory(object):
    template = 'term=&search_title=0&userProjectId=54534&postFilterKeyword=&postTitleSearch=0&blog_numberOfGuestPosts=0&blog_numberOfSponsoredPosts=0&blog_numberOfGiveaways=0&blog_productReview=0&blog_adNetworks=0&blog_twitter=0&twitter_low=&twitter_hi=&blog_facebook=0&facebook_low=&facebook_hi=&blog_googleplus=0&blog_youtube=0&youtube_low=&youtube_hi=&blog_pinterest=0&pinterest_low=&pinterest_hi=&blog_instagram=0&instagram_low=&instagram_hi=&prLow=2&prHigh=10&domainAuthority=&safeSearch=1&lastPostDate=2014-07-23T00%3A00%3A00Z+TO+2014-11-20T00%3A00%3A00Z&blog_numberOfAuthors=&lang=en&_search=false&nd=1416489577997&rows={rows}&page={{page}}&sidx=&sord=asc&query%5B%5D={keyword}~OR&blog_location_adm1Name=&blog_location_countryName=&blog_location_name=&search=true'

    def __init__(self, rows, keyword):
        self.rows = rows
        self.keyword = keyword

    @property
    def partial_template(self):
        "Template partielle avec rows et keyword constantes"

        return self.template.format(rows=self.rows, keyword=self.keyword)

    def generate_by_page(self, page):
        "Generation de formdata pour la n-eme page de resultat"

        raw = self.partial_template.format(page=page)
        return dict(urlparse.parse_qsl(raw))


class ChrisSpider(scrapy.Spider):
    name = 'chris'
    start_urls = ['http://app.grouphigh.com/auth/login/?nxtPg=%2Fblogs%2Fsearch%2F']
    factory = FormDataFactory(rows=250, keyword='finance')

    def parse(self, response):
        "Identification sur la page de login"

        return scrapy.FormRequest.from_response(
        response,
        formdata={'userName': LOGIN, 'password': PASSWORD, 'nxtPg': '/blogs/search/'},
        callback=self.search
    )

    def search_page(self, page=1):
        "Demande les resultats de la n-eme page de recherche"

        return scrapy.FormRequest(
        url='http://app.grouphigh.com/blogs/david-search-data/',
        formdata=self.factory.generate_by_page(page=page),
        callback=self.extract
    )

    def search(self, response):
        "Apres le login, on lance la recherche"

        return self.search_page()

    def extract(self, response):
        "Extraction des donnees"

        json_data = json.loads(response.body)
        current_page = int(json_data['page'])
        total_pages = int(json_data['total'])

        if 'rows' not in json_data:
            print '--------------------------------'
            print 'THE END'
            print '--------------------------------'
            return
        for row in json_data['rows']:
            emails = row['cell'].get('blog_emails', [])
            for email in emails:
                item = ChrisItem()
                item['email'] = email
                item['blog_address'] = row['cell'].get('blog_blogLink', '')
                item['mozrank'] = row['cell'].get('blog_seo_umrp', '')
                yield item
        print '--------------------------------'
        print 'Current page {}, total page: {}'.format(current_page, total_pages)
        print '--------------------------------'
        if current_page < total_pages:
            yield self.search_page(current_page + 1)
