from inspect import istraceback
import discord
import asyncpraw
import os
import random
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from discord.ext import commands
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from lxml import html

# ignoring certain errors that may pop up
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# Setting our browser to use Chrome
driver = webdriver.Chrome(options=options)


# Accessing our desired pages to scrape
# driver.get("https://google.com/")   

# Setting up our connection to discord
client = discord.Client()


# Acquiring access to our Reddit API
reddit = asyncpraw.Reddit(client_id = 'zxKUahTLCzMsqA', 
                     client_secret = 'qUTejPPUoIRo4uHZsZTQ7fVrClCLTA',
                     user_agent = 'Source Collector')


# Variables used to check various properties of reddit posts

image_extensions = ['.png', '.jpg', '.jpeg']
img_title = []
img_url = []
img_karma = []
img_date = []
img_id = []


# setting up bot to register commands that start with an !
bot = commands.Bot(command_prefix='!')

# registering events using a callback

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == bot.user:
        return


# if the user triggers a cooldown, this event will return an error message to the user
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        err = 'Please wait 10 seconds between commands'
        await ctx.send(err)

# Testing bot commands

@bot.command()
async def test(ctx):
    await ctx.send("Command received!")

# list of commands our bot supports
list_cmds = ["!ingredients", "!recipes"]

@bot.command()
async def cmds(ctx):
    await ctx.send("\n".join(list_cmds))

# gathering what recipe our bot will search for
@bot.command()
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user) 
async def ingredients(ctx, *, arg):    

    # begins by getting access to the recipe site we want to use and searches by the users input
    driver.get('https://www.allrecipes.com/search/results/?search=' + arg.replace(" ", "+"))
    
    # locates the search bar
#    search = driver.find_element(By.XPATH, '//input[@id="search-block"]')
        

    time.sleep(5)

    # getting url of our current page, which is going to be the page where the recipes are
    url = driver.current_url
    
    # now creating variable r to get access to our url using BeautifulSoup 
    r = requests.get(url)
    sourcePage = r.content

    soup = BeautifulSoup(sourcePage, 'lxml')
    links = []

    # looping through our web page to find all instances of a certain div
    # followed by inputting all of our links into our list to be accessed
    for i in soup.findAll('div', {"class" : "component card card__recipe card__facetedSearchResult"}):
        link = i.find('a', href=True)
        if link is None:
            continue
        links.append(link)
        print(link['href'])

    # grabbing a random link from our list to display to the user
    # this way they won't see duplicate results as often
    randomNum = random.randint(0, len(links))
   
    await ctx.send(links[randomNum]['href'])

@bot.command()
async def help(ctx):
  embed = discord.Embed(color = discord.Color.orange())
  embed.set_author(name='Help')

  #List of commands
  embed.add_field(name='!Timer',value = 'set a timer   in minutes',inline= False)
  embed.add_field(name='!Ingredients',value='lets you search a recipe with specified ingredient',inline= False)
  
  await ctx.send(embed = embed)


 #starting a timer with argument in minutes
@bot.command()
async def timer(ctx, minutes: int):
    if minutes <0:
      await ctx.send("number can't be a negative")
    else:
      await ctx.send("time set to:"+ str(minutes))
      time.sleep(minutes *60)
      await ctx.send("Timer has ended")

    