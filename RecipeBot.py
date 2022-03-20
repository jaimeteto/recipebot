import discord
import asyncpraw
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from discord.ext import commands

# Features to be implemented as time goes on, current placeholder until sprints begin.

# Setting our browser to use Chrome
driver = webdriver.Chrome()


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
    if message.author == client.user:
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
@commands.cooldown(1, 10, commands.BucketType.user) 
async def ingredients(ctx, *, arg):    

    # begins by getting access to the recipe site we want to use
    driver.get('https://www.allrecipes.com/#')
        
    # locates the search bar
    search = driver.find_element(By.XPATH, '//input[@id="search-block"]')
        
    # inputs the ingredients the user wants into the search bar and searches
    search.send_keys(arg)
    search.send_keys(Keys.RETURN)   
        
    await ctx.send("Found recipes for " + arg)

 #TODO
 # Need a way to randomly retrieve a result, so as to avoid giving the user the same recipe multiple times.
 # Still possible to randomly get the same recipe twice, but likelihood is lower this way   
