# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 19:39:29 2020

@author: david
"""
from datetime import datetime
import pandas as pd
import os
from urllib.parse import urlparse
from flask import Flask, render_template, make_response, request
from newsapi import NewsApiClient
import dateutil.parser as dparser

# Initialises flask application
server = Flask(__name__, static_folder='assets')

countries_code = {
    'Global':None,
    'Argentina':'ar',
    'Australia':'au',
    'Austria':'at',
    'Belgium':'be',
    'Brazil':'br',
    'Bulgaria':'bg',
    'Canada':'ca',
    'China':'cn',
    'Colombia':'co',
    'Cuba':'cu',
    'Czech Republic':'cz',
    'Egypt':'eg',
    'France':'fr',
    'Germany':'de',
    'Greece':'gr',
    'Hong Kong':'hk',
    'Hungary':'hu',
    'India':'in',
    'Indonesia':'id',
    'Ireland':'ie',
    'Israel':'il',
    'Italy':'it',
    'Japan':'jp',
    'Latvia':'iv',
    'Lithuania':'lt',
    'Malaysia':'my',
    'Mexico':'mx',
    'Morocco':'ma',
    'Netherlands':'nl',
    'New Zealand':'nz',
    'Nigeria':'ng',
    'Norway':'no',
    'Philippines':'ph',
    'Poland':'pl',
    'Portugal':'pt',
    'Romania':'ro',
    'Russia':'ru',
    'Saudi Arabia':'sa',
    'Serbia':'rs',
    'Singapore':'sg',
    'Slovakia':'sk',
    'Slovenia':'si',
    'South Africa':'za',
    'South Korea':'kr',
    'Sweden':'se',
    'Switzerland':'ch',
    'Taiwan':'tw',
    'Thailand':'th',
    'Turkey':'tr',
    'UAE':'ae',
    'Ukraine':'ua',
    'United Kingdom':'gb',
    'United States':'us',
    'Venuzuela':'ve',
}


def get_year():
    return datetime.now().year



def update_news(country):  
    # Init
    newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    
    # /v2/top-headlines
    top_headlines = newsapi.get_top_headlines(q='Coronavirus',
                                              #sources='google-news',
                                              country=countries_code.get(country),
                                              language='en'
                                              )
    
    articles = top_headlines['articles']
    
    titles = []
    urls = []
    dates= []
    urlToImages = []
    descriptions = []
    for a in articles:
        titles.append(a['title'])
        urls.append(a['url'])
        urlToImages.append(a['urlToImage'])
        descriptions.append(a['description'])                                                                                      
        
        dates.append(dparser.parse(a['publishedAt'], fuzzy=True).strftime("%d %B %y %H:%M:%S"))
            
    d = {'Title':titles,'Url':urls, 'urlToImage':urlToImages, 'Description':descriptions, 'Date':dates}
    
    news_df = pd.DataFrame(d)

    return news_df

@server.route('/')
@server.route('/home')
def home():
    return render_template('index.html', year=get_year())

@server.route('/privacy-policy')
def policy():
    return render_template('privacy-policy.html')

@server.route('/books')
def books():
    return render_template('books.html')

@server.route('/contact-us')
def about():
    return render_template('contact-us.html')

@server.route("/ads.txt")
def ads_txt():
    return server.send_static_file("ads.txt")

@server.route('/news', methods=['GET', 'POST'])
def news():

    if request.method == 'POST':
        country = request.form["countrys"]
        return render_template('news.html', newsa=update_news(country), countries=list(countries_code.keys()), selected_country=country)

    country = 'Global'
    return render_template('news.html', newsa=update_news(country), countries=list(countries_code.keys()), selected_country=country)

@server.route("/sitemap")
@server.route("/sitemap/")
@server.route("/sitemap.xml")
def sitemap():
    """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
    """
    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc

    # Static routes with static content
    static_urls = list()
    for rule in server.url_map.iter_rules():
        if not str(rule).startswith("/admin") and not str(rule).startswith("/user"):
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {
                    "loc": f"{host_base}{str(rule)}"
                }
                static_urls.append(url)

    xml_sitemap = render_template("sitemap_template.xml", static_urls=static_urls, host_base=host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response
   
# @server.route("/sitemap.xml")
# def sitemap():
#     return render_template("sitemap.xml")

# @server.route('/tracker')
# def tracker():
#     return redirect('/tracker/')

# @server.route('/map')
# def mapout():
#     return redirect('/map/')

# if __name__ == '__main__':
#       #app.run(host='0.0.0.0', port=5000)
#       #app.run(debug=True) #runs on default port 5000
#       server.run(debug=True, use_reloader=False)
#       #server.run()
