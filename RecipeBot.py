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
list_cmds = ["!recipes", "!ingredients", "!exclude", "!convert", "!measurements"]

@bot.command()
async def cmds(ctx):
    await ctx.send("\n".join(list_cmds))

# gathering what recipe our bot will search for
@bot.command(description='Call this command to search for recipes with certain keywords')
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user) 
async def recipes(ctx, *, arg):    
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
        
        # determining in a 1 out of 5 chance to replace the recipe's image with a meme depending on the keyword
        if (randomNum % 5 == 0):
            # locate the specific keyword to associate the correct meme or gif
            if "chocolate" in arg:
                embedRecipe.set_image(url = "https://media3.giphy.com/media/JpehtCvclNLSE/giphy.gif?cid=790b76111a633b4e28035d07ecd58f69587130f7c54cf3e5&rid=giphy.gif&ct=g")
            elif "chips" in arg:
                embedRecipe.set_image(url = "https://c.tenor.com/RuisIo5_WlQAAAAd/awkward.gif")
            elif "sandwich" in arg:
                embedRecipe.set_image(url = "https://c.tenor.com/p98d_YNK3K8AAAAC/gordon-ramsay-idiot-sandwich.gif")
            elif "chili" in arg:
                embedRecipe.set_image(url = "https://c.tenor.com/x_1Gmh_QmHAAAAAd/office.gif")
            elif "pancake" in arg:
                embedRecipe.set_image(url = "https://c.tenor.com/nNuQs8a6O3cAAAAd/pancake-pancake-flip.gif")
            elif "quinoa" in arg:
                embedRecipe.set_image(url = "https://i1.wp.com/i.giphy.com/media/8EpFqeoStLm4FLaWxC/giphy.gif")
            elif "raw" in arg:
                embedRecipe.set_image(url = "https://media2.giphy.com/media/we4Hp4J3n7riw/200w.webp?cid=ecf05e47lqorkq8o2nt0adybjwztql7ggbb1ly3p05m7ucpd&rid=200w.webp&ct=g")
            elif "pan" in arg:
                embedRecipe.set_image(url = "https://c.tenor.com/zYJFQVV7R1AAAAAC/cooking-viralhog.gif")
        
    await ctx.send(embed=embedRecipe)
    
    # asks if the user would like a list of ingredients, getting their response via reactions
    msg = await ctx.send("Would you like a list of ingredients?")
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    # storing ingredients and creating an embed to display to the user
    ingredients = scraper.ingredients()
    embedIngredients = discord.Embed(title='List of Ingredients', description="\n".join(ingredients), color=discord.Colour(0x3498DB))

    # try except statement to figure out what to do based on the users response
    try:
        reaction, user = await bot.wait_for('reaction_add')
        while user == bot.user:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0)
        if str(reaction.emoji) == '✅':
            await ctx.send(embed=embedIngredients)
        elif str(reaction.emoji) == '❌':
            await ctx.send("https://c.tenor.com/okyDOdvpVDcAAAAC/master-chef-gordon-ramsey.gif")
    except asyncio.TimeoutError:
        await ctx.send("")
    
    # new message to ask if the user wants to get another recipe with the same arguments
    msgRefresh = await ctx.send("Would you like a different recipe?")
    await msgRefresh.add_reaction('🔄')
    await msgRefresh.add_reaction('❌')
    # check if the user responded with a refresh emoji
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '🔄'
    # try except statement to decide on recalling the command again
    try:
        await bot.wait_for('reaction_add', timeout=10.0, check=check)
        await recipes(ctx = ctx, arg = arg)
    except asyncio.TimeoutError:
        await ctx.send("")

# gathering what recipe our bot will search for
@bot.command(description='Call this command to search for recipes with certain ingredients')
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user)
async def ingredients(ctx, *, arg):
    async with ctx.typing():

        # begins by getting access to the recipe site we want to use and searches by the users input

        # getting url of our current page, which is going to be the page where the recipes are
        url = 'https://www.allrecipes.com/search/results/?search=&IngIncl=' + arg.replace(" ", "&IngIncl=")

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
       
    # asks if the user would like a list of ingredients, getting their response via reactions
    msg = await ctx.send("Would you like a list of ingredients?")
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    # storing ingredients and creating an embed to display to the user
    ingredients = scraper.ingredients()
    embedIngredients = discord.Embed(title='List of Ingredients', description="\n".join(ingredients), color=discord.Colour(0x3498DB))

    # try except statement to figure out what to do based on the users response
    try:
        reaction, user = await bot.wait_for('reaction_add')
        while user == bot.user:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0)
        if str(reaction.emoji) == '✅':
            await ctx.send(embed=embedIngredients)
        elif str(reaction.emoji) == '❌':
            await ctx.send("https://c.tenor.com/okyDOdvpVDcAAAAC/master-chef-gordon-ramsey.gif")
    except asyncio.TimeoutError:
        await ctx.send("")
    
    # new message to ask if the user wants to get another recipe with the same arguments
    msgRefresh = await ctx.send("Would you like a different recipe?")
    await msgRefresh.add_reaction('🔄')
    await msgRefresh.add_reaction('❌')
    # check if the user responded with a refresh emoji
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '🔄'
    # try except statement to decide on recalling the command again
    try:
        await bot.wait_for('reaction_add', timeout=10.0, check=check)
        await recipes(ctx = ctx, arg = arg)
    except asyncio.TimeoutError:
        await ctx.send("")
            
# gathering what recipe our bot will search for
@bot.command(description='Call this command to search for recipes with certain ingredients')
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user)
async def exclude(ctx, *, arg):
    async with ctx.typing():

        # begins by getting access to the recipe site we want to use and searches by the users input

        # getting url of our current page, which is going to be the page where the recipes are
        url = 'https://www.allrecipes.com/search/results/?search=&IngExcl=' + arg.replace(" ", "&IngExcl=")

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


    # asks if the user would like a list of ingredients, getting their response via reactions
    msg = await ctx.send("Would you like a list of ingredients?")
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    # storing ingredients and creating an embed to display to the user
    ingredients = scraper.ingredients()
    embedIngredients = discord.Embed(title='List of Ingredients', description="\n".join(ingredients), color=discord.Colour(0x3498DB))

    # try except statement to figure out what to do based on the users response
    try:
        reaction, user = await bot.wait_for('reaction_add')
        while user == bot.user:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0)
        if str(reaction.emoji) == '✅':
            await ctx.send(embed=embedIngredients)
        elif str(reaction.emoji) == '❌':
            await ctx.send("https://c.tenor.com/okyDOdvpVDcAAAAC/master-chef-gordon-ramsey.gif")
    except asyncio.TimeoutError:
        await ctx.send("")
    
    # new message to ask if the user wants to get another recipe with the same arguments
    msgRefresh = await ctx.send("Would you like a different recipe?")
    await msgRefresh.add_reaction('🔄')
    await msgRefresh.add_reaction('❌')
    # check if the user responded with a refresh emoji
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '🔄'
    # try except statement to decide on recalling the command again
    try:
        await bot.wait_for('reaction_add', timeout=10.0, check=check)
        await recipes(ctx = ctx, arg = arg)
    except asyncio.TimeoutError:
        await ctx.send("")
          
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
      
# give a table containing all conversions for the user input
@bot.command(description='Call this command to convert a number from one unit of measurement to another.'\
    + '\n Type in a valid **value**, **units** of that value, and the **desired units** to convert to.')
async def convert(ctx, *args):
    async with ctx.typing():

        # checking if any of the arguments are about temperature, which is not included in the website
        if (args[1] == 'c' and args[2] == 'f') or (args[1] == 'f' and args[2] == 'c'):
            # formula for celsius to fahrenheit
            if args[1] == 'c':
                result = (float(args[0]) * 1.8) + 32
            # formula for fahrenheit to celsius
            else:
                result = (float(args[0]) - 32) * 0.5556

            # send the conversion in a nice formatted message with a title and conversion
            embedConvert = discord.Embed(title = 'Conversion: **' + args[1] + '** → **' + args[2]\
             + '**', description = '```' + str(result) + '°' + args[2] + '```')

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

            # send the conversion in a nice formatted message with a tile and conversion
            embedConvert = discord.Embed(title = 'Conversion: **' + args[1] + '** → **' + args[2] + '**', \
                description = '```' + conversion + ' ' + args[2] + '```', color = discord.Colour(0xDC143C))

    await ctx.send(embed = embedConvert)

@bot.command(description = 'Call this command in order to find out all valid inputs to the !convert command')
async def measurements(ctx):

    # list containing a the valid arguments for the !convert command
    options = ['————————————————————————————————————',
               '\t\tVolume Measurements',
               '————————————————————————————————————',
               'Teaspoons (tsp):          teaspoon',
               'Tablespoons (Tbsp):       tablespoon',
               'Gills (gi):               gill',
               'Imperial Gills (gi):      UK+gill',
               'Cups (c):                 cup',
               'Imperial Cups (c):        UK+cup',
               'Pints (pt):               pint',
               'Imperial Pints (pt):      UK+pint',
               'Imperial Quarts (qt):     UK+quart',
               'Gallons (gal):            gal',
               'Imperial Gallons (gal):   UK+gal',
               '————————————————————————————————————',
               '\t\tWeight Measurements',
               '————————————————————————————————————',
               'Ounces (oz):              oz',
               'Fluid Ounces (fl. oz.):   fluid+oz',
               'Grains (gr):              grain',
               'Grams (g):                g',
               'Decagrams (dag):          decagram',
               'Kilograms (kg):           kg',
               'Pounds (lb):              lb',
               '————————————————————————————————————',
               '\t  Temperature Measurements',
               '————————————————————————————————————',
               'Celsius (°C):             c',
               'Fahrenheit (°F):          f',]

    d = '```' + '\n'.join(options) + '```'

    embedUnits = discord.Embed(title = 'Supported Cooking Measurements', description = d, color = discord.Colour(0xDC143C))
    await ctx.send(embed = embedUnits)

    
bot.run('OTUyMjg0NjE1NTM0NTgzODA4.YizyKA.3fnwxAhIObzZBV_FZ04DsjwSgEM')
