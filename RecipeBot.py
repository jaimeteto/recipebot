import discord
import asyncpraw
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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




# registering events using a callback

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

# Testing bot commands

    if message.content.startswith("!test"):
        await message.channel.send("Command received!")


#    if message.content.startswith("!commands"):
 #       await message.channel.send()

# gathering what recipe our bot will search for

    # begins by separating our actual recipe string
    if message.content.startswith("!ingredients"):
        
        # gathers the string that we care about following our command
        content = message.content.split("!ingredients ")[1]
        
        # begins by getting access to the recipe site we want to use
        driver.get('https://www.allrecipes.com/#')
        
        # locates the search bar
        search = driver.find_element_by_xpath('//input[@id="search-block"]')
        
        # inputs the ingredients the user wants into the search bar and searches
        search.send_keys(content)
        search.send_keys(Keys.RETURN)
        await message.channel.send("Found recipes for " + content)

      
      
      
      
   
