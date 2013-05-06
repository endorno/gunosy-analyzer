#! /usr/bin/env python
# -*- coding:utf-8 -*-
import json
import re
import urllib2
import datetime
import tweepy
from scrapemark import scrape
import urllib
from prettyprint import pp

url_analyzer = re.compile('http://gunosy.com/(.*?)/.*')
search_query = u"のGunosy via"

def find_gunosy_accounts():
    api = tweepy.API()
    gunosy_accounts = set()
    for tweet in tweepy.Cursor(api.search,
                               q=search_query,
                               rpp=100,
                               result_type="recent",
                               include_entities=True,
                               lang="ja").items():
        for entity in tweet.entities['urls']:
            url = entity['expanded_url']
            result = url_analyzer.search(url)
            if result:
                gunosy_accounts.add(result.group(1))
    gunosy_accounts = list(gunosy_accounts)
    print "----use following accounts-----"
    pp(gunosy_accounts)
    return gunosy_accounts

def extract_recommended_urls(gunosy_url):
    try:
        articles = scrape("""
        {*
        <div class='art_text_wrap'>
        {*
        <a href='{{ [article].url }}'>
        <h1>{{ [article].title }}</h1>
        </a>
        *}
        </div>
        *}
        """,url=gunosy_url)
    except:
        #TODO error handling
        return []
    urls = []
    for article in articles['article']:
        if article.has_key('title') and article['title'] is not None:
            urls.append(article['url'])
    return urls

def get_time_hatebed_at(url):
    u"""
    return datetime
    if not hatebed, return None
    """
    endpoint = "http://b.hatena.ne.jp/entry/jsonlite/?"
    encoded_url = urllib.quote_plus(url.replace("#","%23"))
    request_api = endpoint+"url="+encoded_url
    try:
        data = json.load(urllib2.urlopen(request_api))
    except:
        #TODO error handling
        return None
    oldest_hatebed_time = None
    if data is not None:
        for bukuma in data['bookmarks']:
            t = datetime.datetime.strptime(bukuma['timestamp'],'%Y/%m/%d %H:%M:%S')
            if oldest_hatebed_time is None or oldest_hatebed_time > t:
                oldest_hatebed_time = t
    return oldest_hatebed_time

def main():
    accounts = find_gunosy_accounts()[:100]
    print "will analyze %d user"%len(accounts)

    delivered = datetime.datetime(2013,5,5,8,0,0)
    delivered_before_hatebed_urls=[]
    delivered_after_hatebed_urls =[]
    for account in accounts:
        recommended_urls = extract_recommended_urls("http://gunosy.com/%s/%d/%02d/%02d"%(account,delivered.year,delivered.month,delivered.day))
        for recommended_url in recommended_urls:
            hatebed = get_time_hatebed_at(recommended_url)
            if hatebed is None or hatebed > delivered:
                print "\nurl:%s\nhatebed at:%s\ndelivered at:%s"%(recommended_url,hatebed,delivered)
                delivered_before_hatebed_urls.append(recommended_url)
            else:
                delivered_after_hatebed_urls.append(recommended_url)
    print "before:",len(delivered_before_hatebed_urls)
    print "after:",len(delivered_after_hatebed_urls)



if __name__ == "__main__":
    main()

