#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import logging
import requests
from BeautifulSoup import BeautifulSoup

base_url = "http://www.tripadvisor.com/"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36"
datadir = "data/"
target_city = ""

def get_city_page(base_url, city, state):
    """ Returns the URL of the list of the hotels in a city. Corresponds to
    STEP 1 & 2 of the slides.

    Parameters
    ----------
    city : str
    state : str

    Returns
    -------
    url : str
        The relative link to the website with the hotels list.
    """
    # Build the request URL
    url = base_url + "city=" + city + "&state=" + state
    # Request the HTML page
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    html = response.text.encode('utf-8')
    with open(os.path.join(datadir, city + '-tourism-page.html'), "w") as h:
        h.write(html)

    # Use BeautifulSoup to extract the url for the list of hotels in
    # the city and state we are interested in.

    # For example in this case we need to get the following href
    # <li class="hotels twoLines">
    # <a href="/Hotels-g60745-Boston_Massachusetts-Hotels.html" data-trk="hotels_nav">...</a>
    soup = BeautifulSoup(html)
    li = soup.find("li", {"class": "hotels twoLines"})
    city_url = li.find('a', href=True)
    return city_url['href']


def get_hotellist_page(base_url, city_url, page_count):
    """ Returns the hotel list HTML. The URL of the list is the result of
    get_city_page(). Also, saves a copy of the HTML to the disk. Corresponds to
    STEP 3 of the slides.

    Parameters
    ----------
    city_url : str
        The relative URL of the hotels in the city we are interested in.
    page_count : int
        The page that we want to fetch. Used for keeping track of our progress.

    Returns
    -------
    html : str
        The HTML of the page with the list of the hotels.
    """
    url = base_url + city_url
    # Sleep 2 sec before starting a new http request
    time.sleep(2)
    # Request page
    headers = { 'User-Agent' : user_agent }
    response = requests.get(url, headers=headers)
    html = response.text.encode('utf-8')
    # Save the webpage
    with open(os.path.join(datadir, target_city + '-hotelist-' + str(page_count) + '.html'), "w") as h:
        h.write(html)
    return html


def parse_hotellist_page(html):
    """Parses the website with the hotel list and prints the hotel name, the
    number of stars and the number of reviews it has. If there is a next page
    in the hotel list, it returns a list to that page. Otherwise, it exits the
    script. Corresponds to STEP 4 of the slides.

    Parameters
    ----------
    html : str
        The HTML of the website with the hotel list.

    Returns
    -------
    URL : str
        If there is a next page, return a relative link to this page.
        Otherwise, exit the script.
    """
    soup = BeautifulSoup(html)
    # Extract hotel name, star rating and number of reviews
    hotel_boxes = soup.findAll('div', {'class' :'listing wrap reasoning_v5_wrap jfy_listing p13n_imperfect'})
    if not hotel_boxes:
        print("#################################### Option 2 ######################################")
        hotel_boxes = soup.findAll('div', {'class' :'listing_info jfy'})
    if not hotel_boxes:
        print("#################################### Option 3 ######################################")
        hotel_boxes = soup.findAll('div', {'class' :'listing easyClear  p13n_imperfect'})

    for hotel_box in hotel_boxes:
        hotel_name = hotel_box.find("a", {"target" : "_blank"}).find(text=True)
        print("Hotel name: %s" % hotel_name.strip())

        stars = hotel_box.find("img", {"class" : "sprite-ratings"})
        if stars:
            print("Stars: %s" % stars['alt'].split()[0])

        num_reviews = hotel_box.find("span", {'class': "more"}).findAll(text=True)
        if num_reviews:
            print("Number of reviews: %s " % [x for x in num_reviews if "review" in x][0].strip())

    # Get next URL page if exists, otherwise exit
    #div = soup.find("div", {"class" : "unified pagination "})
    div = soup.find("div", {"class" : "pagination paginationfillbtm"})

    # check if this is the last page
    if div.find('span', {'class' : 'guiArw pageEndNext'}):
        print("We reached last page")
        return None
    # If not, return the url to the next page
    hrefs = div.findAll('a', href= True)
    for href in hrefs:
        if href.find(text = True) == '&raquo;':
            print("Next url is %s" % href['href'])
            return href['href']
			

def parse_hotellist_page2(html,url_list):
    """Parses the website with the hotel list and collects links to each hotel. If there is a next page
    in the hotel list, it returns a link to that page. Otherwise, it exits the
    script.

    Parameters
    ----------
    html : str
        The HTML of the website with the hotel list.

    Returns
    -------
    URL : str
        If there is a next page, return a relative link to this page.
        Otherwise, exit the script.
    """
    soup = BeautifulSoup(html)
    # Extract hotel name, star rating and number of reviews
    hotel_boxes = soup.findAll('div', {'class' :'listing wrap reasoning_v5_wrap jfy_listing p13n_imperfect'})
    if not hotel_boxes:
        print("#################################### Option 2 ######################################")
        hotel_boxes = soup.findAll('div', {'class' :'listing_info jfy'})
    if not hotel_boxes:
        print("#################################### Option 3 ######################################")
        hotel_boxes = soup.findAll('div', {'class' :'listing easyClear  p13n_imperfect'})

    for hotel_box in hotel_boxes:
        hotel_link = hotel_box.find("a", {"target" : "_blank"})
        hotel_link = hotel_link['href']
        if hotel_link is not None:
            url_list.append(hotel_link.strip())

    # Get next URL page if exists, otherwise exit
    #div = soup.find("div", {"class" : "unified pagination "})
    div = soup.find("div", {"class" : "pagination paginationfillbtm"})

    # check if this is the last page
    if div.find('span', {'class' : 'guiArw pageEndNext'}):
        print("We reached last page")
        return None
    # If not, return the url to the next page
    hrefs = div.findAll('a', href= True)
    for href in hrefs:
        if href.find(text = True) == '&raquo;':
            print("Next url is %s" % href['href'])
            return href['href']			


def main(city,state):
    print ("Searching for hotels in {} {}.".format(city,state))
    target_city = city #set global var
	
    # Get current directory
    current_dir = os.getcwd()
    # Create datadir if does not exist
    if not os.path.exists(os.path.join(current_dir, datadir)):
        os.makedirs(os.path.join(current_dir, datadir))

    # Get URL to obtain the list of hotels in a specific city
    city_url = get_city_page(base_url, city, state)
    c=0
    while(True):
        if city_url is None:
            print "***The End***" 
            break
        else:	
            c +=1
            html = get_hotellist_page(base_url,city_url,c)
            city_url = parse_hotellist_page(html)
		
def get_url_list(city,state):
    target_city = city #set global var
	
    # Get current directory
    current_dir = os.getcwd()
    # Create datadir if does not exist
    if not os.path.exists(os.path.join(current_dir, datadir)):
        os.makedirs(os.path.join(current_dir, datadir))

    # Get URL to obtain the list of hotels in a specific city
    city_url = get_city_page(base_url, city, state)
    c=0
    url_list = []
    while(True):
        if city_url is None:
            break
        else:	
            c +=1
            html = get_hotellist_page(base_url,city_url,c)
            city_url = parse_hotellist_page2(html,url_list)
    return url_list