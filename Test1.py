#file use for testing logic of each fucntion

from inspect import istraceback
from tkinter import Image
import discord
import asyncpraw
import os
import random
import time
import requests
import re
import cchardet
import lxml
import asyncio
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from discord.ext import commands
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
from discord_components import DiscordComponents,ComponentsBot,Button,SelectOption,Select




def convert(*args):
    

    # checking if any of the arguments are about temperature, which is not included in the website
    if (args[1] == 'c' and args[2] == 'f') or (args[1] == 'f' and args[2] == 'c'):
        # formula for celsius to fahrenheit
        if args[1] == 'c':
            result = (float(args[0]) * 1.8) + 32
        # formula for fahrenheit to celsius
        else:
            result = (float(args[0]) - 32) * 0.5556

        

    else:
        # begins by getting access to the calculator site we want to use and searches by the users input

        # getting url of our current page, which is going to be the page where the conversion takes place
        url = 'http://www.calcul.com/show/calculator/cooking-conversion?input=' + '%7C'.join(args)

        # now creating variable r to get access to our url using BeautifulSoup
        r = requests.get(url)
        sourcePage = r.text
        soup = BeautifulSoup(sourcePage, 'lxml')

        # retrieving the result of the conversion and processing the string
        result = soup.find('span', {"class" : "result"})
        conversion = (result.string).replace('\\', '').replace('(', '').replace(')', '')
        result = conversion

    
    return result
       


# position arg: position in the array of all recipes
def ingredients(arg,position):


    # begins by getting access to the recipe site we want to use and searches by the users input

    # getting url of our current page, which is going to be the page where the recipes are
    url = 'https://www.allrecipes.com/search/results/?search=&IngIncl=' + arg.replace(" ", "&IngIncl=")

    # now creating variable r to get access to our url using BeautifulSoup
    r = requests.get(url)
    sourcePage = r.text

    soup = BeautifulSoup(sourcePage, 'lxml')

    # handling the cases where the users search might yield no results
    check_result = soup.findAll('div', {"class" : "searchResults__noResultsContainer"})
    for x in check_result:
        if (x.find('p').text.strip() == 'Check your spelling, try a more generic term, or less terms'):
           
            return "No results found, please try again"


    # going through our web page to find all instances of a certain div
    random_link = soup.findAll('div', {"class" : "component card card__recipe card__facetedSearchResult"})
    
    links = random_link[position].find('a', href=True)

    scraper = scrape_me(links['href'])
    
    return links['href']


#argument number is the position in the array of recipes.
def search(category, number):

    #categories urls (breakfast, lunch, dinner)
    lunch ='https://www.allrecipes.com/recipes/17561/lunch/'
    breakfast ='https://www.allrecipes.com/recipes/78/breakfast-and-brunch/'
    dinner = 'https://www.allrecipes.com/recipes/17562/dinner/'
    mexican = 'https://www.allrecipes.com/recipes/728/world-cuisine/latin-american/mexican/'
    chinese = 'https://www.allrecipes.com/recipes/695/world-cuisine/asian/chinese/'
    italian = 'https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/'
    lowcalorie = 'https://www.allrecipes.com/recipes/1232/healthy-recipes/low-calorie/'

    Mainurl =''

    #getting driver according to category
    if category == "lunch":
        Mainurl = lunch
    elif category== "breakfast":
        Mainurl=breakfast
    elif category== "dinner":
        Mainurl=dinner
    elif category== "mexican":
        Mainurl = mexican
    elif category =="chinese":
        Mainurl = chinese
    elif category =="italian":
        Mainurl = italian
    elif category ==("lowCalorie"):
        Mainurl = lowcalorie
    #getting url of our current page, which is going to be the page where the recipes are
    #url = driver.current_url
    
    # now creating variable r to get access to our url using BeautifulSoup 
    r = requests.get(Mainurl)
    sourcePage = r.content

    soup = BeautifulSoup(sourcePage, 'lxml')
    
    # going through web page to find all instances of a certain div and limiting to 10 for speed pursposes 
    random_link = soup.findAll('a', {"class" : "card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"}, limit = 10)
    #print(random_link)
    # grabbing a random link from our list to display to the user
    # this way they won't see duplicate results as often
    #randomNum = random.randint(0, len(random_link)-1)
    #getting link from div
    link = random_link[number].get('href')
        
    scraper = scrape_me(link)
    
        
    #getting access to our desired recipe page to scrape more information
    r = requests.get(link)
    sourcePage = r.content
    soup = BeautifulSoup(sourcePage, 'lxml')


    # scraping through the page to find a description
    desc = soup.find('p', {"class" : "margin-0-auto"})

   
     
   
    return link 

# test timer for displaying
def timer1(minutes:int,seconds=0):


    totalTime= ((minutes*60) + seconds)

    #time in seconds since Unix epoch
    currentTime = time.time()
    targetTime = totalTime + currentTime
   
    
    
    # no negative inputs
    if minutes <0 or seconds< 0:
        return "number can't be a negative"
    else:

        # loop used to display and edit timer in message
        
        currentTime = time.time()
        timeDifference = targetTime - currentTime
        
        return f"{int(timeDifference/60)}:{int(60*((timeDifference/60)-int(timeDifference/60)))}"

# test timer for accuracy
def timer2(minutes:int,seconds=0):

    t0 = time.time()
    totalTime= ((minutes*60) + seconds)

    #time in seconds since Unix epoch
    currentTime = time.time()
    targetTime = totalTime + currentTime
   
    
    
    # no negative inputs
    if minutes <0 or seconds< 0:
        return "number can't be a negative"
    else:

        # loop used to display and edit timer in message
         while targetTime>currentTime:
            currentTime = time.time()

            #difference between times
            timeDifference = targetTime - currentTime

        
    # checking timer acuracy.( this is the time that the while loop took to terminate)   
    t1 = time.time()- t0
      
    return int(t1)



#testing function for search used in the categories fucntion
def TestingSearch():

    #links of recipes as shown in webpage
    #first two recipes in the Lunch categories
    link1 = 'https://www.allrecipes.com/recipe/20185/virginas-tuna-salad/'
    link2 = 'https://www.allrecipes.com/recipe/85901/spicy-grilled-cheese-sandwich/'

    #fisrt 2 links in the 
    #testing that search is returning from the correct webpage
    assert search("lunch",0) == link1
    assert search("lunch",1)== link2


#testing display and accuracy for timer
def TestingTimer():
    #testing dispaly
    assert timer1(5,0) == "5:0"
    assert timer1(100,9)== "100:9"
    assert timer1(0,7)== "0:7"

    
#testing timer for accuracy
def TestingTimer2():

    #5 min == 300 secs
    assert int(timer2(0,10)) == 10
    assert int(timer2(1,0))== 60



#fucntion used to check if ingredient is in the recipe is given by the ingredients fucntion
def wordFinder(ingredientInput):

    
    link1 = ingredients(ingredientInput,1)
    scraper = scrape_me(link1)

    ingredients1 = scraper.ingredients()

    for i in ingredients1:
        if ingredientInput in i:
            return True
    return False

#testing ingredients fucntion

def TestingIngredients():
    assert wordFinder('chocolate')
    assert wordFinder('onion')
    assert wordFinder('tomato')


    

def TestingCoverter():
    assert int(convert(5,'c','f')) == 41
    assert float(convert('10', 'oz','g')) == 283.50



if __name__ == "__main__":
    TestingSearch()
    TestingTimer()
    TestingTimer2()
    TestingIngredients()
    TestingCoverter()

    

    print("All tests passed")

