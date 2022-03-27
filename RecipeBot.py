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
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from discord.ext import commands
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me


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
        err = 'Please wait 5 seconds between commands'
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
@bot.command(description='Call this command to search for recipes with certain ingredients')
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user) 
async def ingredients(ctx, *, arg):    
    async with ctx.typing():

        # begins by getting access to the recipe site we want to use and searches by the users input

        # getting url of our current page, which is going to be the page where the recipes are
        url = 'https://www.allrecipes.com/search/results/?search=' + arg.replace(" ", "+")
    
        # now creating variable r to get access to our url using BeautifulSoup 
        r = requests.get(url)
        sourcePage = r.text

        soup = BeautifulSoup(sourcePage, 'lxml')

        # going through our web page to find all instances of a certain div
        random_link = soup.findAll('div', {"class" : "component card card__recipe card__facetedSearchResult"})
        # grabbing a random link from our list to display to the user
        # this way they won't see duplicate results as often
        randomNum = random.randint(0, len(random_link))
        links = random_link[randomNum].find('a', href=True)
        
        scraper = scrape_me(links['href'])
    
        
        # getting access to our desired recipe page to scrape more information
        r = requests.get(links['href'])
        sourcePage = r.text
        soup = BeautifulSoup(sourcePage, 'lxml')

        # scraping through the page to find a description
        desc = soup.find('p', {"class" : "margin-0-auto"})
    
        # sending a formatted message with the recipes title, description, link, and image
        embedRecipe = discord.Embed(title=scraper.title(), description="{}".format(desc.text), color=discord.Colour(0x8A2BE2), url = links['href'])
        embedRecipe.set_image(url="{}".format(scraper.image()))
        
        
    await ctx.send(embed=embedRecipe)

# sort of overwriting help command to follow a certain format
class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        # gets all of our commands, and adds its description to our help command
        destination = self.get_destination()
        eb = discord.Embed(color=discord.Color.green(), description='')
        for page in self.paginator.pages:
            eb.description += page
        await destination.send(embed=eb)

bot.help_command = HelpCommand()



 #starting a timer with argument in minutes
@bot.command(description='A timer to help with tracking time')
async def timer(ctx, minutes: int):
    if minutes <0:
      await ctx.send("number can't be a negative")
    else:
      await ctx.send("time set to:"+ str(minutes))
      time.sleep(minutes *60)
      await ctx.send("Timer has ended")

    
bot.run('OTUyMjg0NjE1NTM0NTgzODA4.YizyKA.3fnwxAhIObzZBV_FZ04DsjwSgEM')
