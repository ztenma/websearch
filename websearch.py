#! /usr/bin/env python3

import urllib.request
import html.parser

class SearchResult():
    
    def __init__(self, url, title):
        self.url = url
        self.title = title
    
    def __str__(self):
        return '%r, %r)' % (self.url, self.title)
    
    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.url, self.title)

class WebSearch():
    """Abstract class"""
    
    def __init__(self, baseUrl, parserKlass):
        self.baseUrl = baseUrl
        self.parser = parserKlass()
        userAgent = 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
        self.headers = {'User-Agent': userAgent}
        print('base url:', self.baseUrl)
        
    def formatUrl(self, keyword, count):
        raise NotImplementedError
    
    def getCharset(self, response):
        return response.headers.get('Content-Type', 'text/html; charset=UTF-8').split('=')[1].strip()
    
    def search(self, keyword, count=10):
        results = []
        req = urllib.request.Request(self.formatUrl(keyword, count), headers=self.headers)
        res = urllib.request.urlopen(req)
        print('url:', res.url, '\ncode:', res.code)
        
        if res.code == 200:
            data = res.read().decode(self.getCharset(res))
            self.parser.feed(data)
            results = self.parser.getResults()
        return results


class WikipediaSearch(WebSearch):
    def __init__(self, base="en.wikipedia.org", ssl=False):
        WebSearch.__init__(self,
            "http{}://{}/w/index.php?search=%{{}}&title=Special:Search&limit={{}}"
            .format('s' if ssl else '', base), WikipediaParser)
            
    def formatUrl(self, keyword, count):
        return self.baseUrl.format('%' + keyword, count) 

class GoogleSearch(WebSearch):
    def __init__(self, base="www.google.com"):
        WebSearch.__init__(self,
            "https://{}/search?q={{}}&num={{}}".format(base), GoogleParser)
        
    def formatUrl(self, keyword, count):
        return self.baseUrl.format(keyword, count)

class WebSearchParser(html.parser.HTMLParser):
    
    HTMLVoidElements = ['meta', 'link', 'param', 'source', 'br', 'hr', 'img', 
    'input', 'embed', 'area', 'base', 'col', 'command', 'keygen', 'track', 'wbr']
    
    def __init__(self):
        super().__init__()
        
        self.results = []
        self.depth = 0
    
    def handle_starttag(self, tag, attrs):
        #print(".", end='')
        #if 'a' == tag:
            #print("tag:", tag)
            #print("attrs:", attrs)
        if tag not in WebSearchParser.HTMLVoidElements:
            self.depth += 1
            
    def handle_endtag(self, tag):
        if tag not in WikipediaParser.HTMLVoidElements:
            self.depth -= 1
            
    def tagGetAttr(attrName, attrNames):
        for attr, val in attrNames:
            if attr == attrName:
                return val
                
    def inAttributes(attrs, attr, val=None):
        return any(attr == curAttr and val in (curVal, None) for curAttr, curVal in attrs)
                
    def getResults(self):
        return self.results

class WikipediaParser(WebSearchParser):

    def __init__(self):
        super().__init__()
        
        self.resultsSectionDepth = -1
        self.inResultsSection = False
    
    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if tag == 'ul' and WebSearchParser.inAttributes(attrs, 'class', 'mw-search-results'):
            self.resultsSectionDepth = self.depth - 1
            self.inResultsSection = True
        elif self.inResultsSection and 'a' == tag:
            url = WebSearchParser.tagGetAttr('href', attrs)
            title = WebSearchParser.tagGetAttr('title', attrs)
            #print("url %s title %s" % (url, title))
            self.results.append(SearchResult(url, title))
            
    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if self.inResultsSection and self.depth == self.resultsSectionDepth:
            self.inResultsSection = False

class GoogleParser(WebSearchParser):

    def __init__(self):
        super().__init__()
        
        self.resultsItemDepth = -1
        self.inResultsItem = False
    
    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if tag == 'h3' and WebSearchParser.inAttributes(attrs, 'class', 'r'):
            self.resultsItemDepth = self.depth - 1
            self.inResultsItem = True
        elif self.inResultsItem and tag == 'a':
            url = WebSearchParser.tagGetAttr('href', attrs)
            #print("url %s title %s" % (url, None))
            self.results.append(SearchResult(url, None))

    def handle_data(self, data):
        if self.inResultsItem:
            self.results[-1].title = data
            
    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if self.inResultsItem and self.depth == self.resultsItemDepth:
            self.inResultsItem = False

if __name__ == '__main__':
    #print(WikipediaSearch().search('ram'))
    res = GoogleSearch().search('ram')
    for r in res:
        print(r)
