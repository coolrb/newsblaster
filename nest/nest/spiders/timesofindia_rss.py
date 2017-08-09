import scrapy
import urllib2
import re
from datetime import datetime
from scrapy.spiders import XMLFeedSpider
from scrapy.selector import Selector
import sys
from nest.news_parser import ArticleExtractor
from bs4 import BeautifulSoup


class NewyorkTimesRssSpider(XMLFeedSpider):

    name = "timesofindia_rss"
    allowed_domains = ["timesofindia.com"]
    download_delay = 2

    start_urls = (
        'http://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'http://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
        'http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',
        'http://timesofindia.indiatimes.com/rssfeeds/296589292.cms')

    itertag = 'item'

    def parse_node(self, response, node):
        # Clean up namespace to allow for tags to be accessed
 
        node.remove_namespaces()
        #titles = node.xpath('//title/text()').extract()
        #title= titles[2]
        #description = node.xpath('//*[name()="media:description"]/text()').extract()
        #description = node.xpath('//description/text()').extract()
        pub_date = ''
        links = node.xpath('//link/text()').extract()
        pub_dates = node.xpath('//pubDate/text()').extract()
        small_img = node.xpath('//*[name()="media:content"]/@url').extract()
        
        #TODO Convert date
        if len(links) > 0:
            pub_date = pub_dates[0]

        # Fetch actual article
        if len(links) > 0:

            url = links[0]

            # Cookie workaround for NY Times. NY times a ...
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            response = opener.open(url)
            raw_html = response.read()

            # Goose cannot extract clean text from html of NY Times
            soup = BeautifulSoup(raw_html,"lxml")
            story_body =  soup.findAll("div", class_="main-content")
            story_texts = []
            for story_text in story_body:
                story_texts.append(story_text.get_text())

            cleaned_text = ' '.join(story_texts)

            article_ex = ArticleExtractor(url,response,raw_html)
            article_item = article_ex.get_article_item()

            # Override since Goose was not able to extract correctly
            article_item['text_content'] = cleaned_text
            article_item['date_published'] = pub_date
            article_item['source'] = 'timesofindia'
            return article_item

