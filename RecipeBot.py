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

# ignoring certain errors that may pop up
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--headless")

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
bot = commands.Bot(command_prefix='!', help_command=None)



#starting dicordComponets on bot
DiscordComponents(bot)



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

    # begins by getting access to the recipe site we want to use and searches by the users input

    # getting url of our current page, which is going to be the page where the recipes are
    url = 'https://www.allrecipes.com/search/results/?search=' + arg.replace(" ", "+")
    
    # now creating variable r to get access to our url using BeautifulSoup 
    r = requests.get(url)
    sourcePage = r.text
    soup = BeautifulSoup(sourcePage, 'lxml')
        
    # handling the cases where the users search might yield no results
    check_result = soup.findAll('div', {"class" : "searchResults__noResultsContainer"})
    for i in check_result:
        if (i.find('p').text.strip() == 'Check your spelling, try a more generic term, or less terms'):
            await ctx.trigger_typing()
            await asyncio.sleep(0.5)
            await ctx.send("No results found, please try again")
            return
        
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
            if (randomNum % 2 == 0):
                embedRecipe.set_image(url = "https://c.tenor.com/8PHh0EUxLFwAAAAM/drop-down-failarmy.gif")
            else:
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
        elif "hotdog" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/GB-11l60LwYAAAAd/hotdog-fingers-playing-with-meat.gif")
        elif "pizza" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/9q7E1GsL-hQAAAAd/wasted-pizza-failarmy.gif")
        elif "salad" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/Fyf-HQ5CgZcAAAAC/salad-funny.gif")
        elif "fries" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/rUdNSJQOiU8AAAAC/dechartgames-hungry-garden.gif")
    
    button_Ing = Button(label="Ingredients", style="2", custom_id="b1")
    button_Stop = Button(label="Stop", style="2", custom_id="b2")
    button_Ref = Button(label="Refresh", style="2", custom_id="b3")

    await ctx.trigger_typing()
    await asyncio.sleep(0.5)
    await ctx.send(embed=embedRecipe, components=[[button_Ing, button_Stop, button_Ref]])
    # storing ingredients and creating an embed to display to the user
    ingredients = scraper.ingredients()
    embedIngredients = discord.Embed(title='List of Ingredients', description="\n".join(ingredients), color=discord.Colour(0x3498DB))
    embedStop = discord.Embed()
    embedStop.set_image(url="https://c.tenor.com/okyDOdvpVDcAAAAC/master-chef-gordon-ramsey.gif")
    embed_no = discord.Embed(title="", description="")

    interaction = await bot.wait_for("button_click")
    if (interaction.component.custom_id == "b1"):
        await interaction.respond(embed=embedIngredients, ephemeral=False)
    elif (interaction.component.custom_id == "b2"):
        await interaction.respond(embed=embedStop, ephemeral=False)
    elif (interaction.component.custom_id == "b3"):
        await interaction.defer(ephemeral= False)
        await recipes(ctx = ctx, arg = arg)
        await interaction.respond(embed=embed_no)
            

    
# gathering what recipe our bot will search for
@bot.command(description='Call this command to search for recipes with certain ingredients')
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user)
async def ingredients(ctx, *, arg):


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
            await ctx.trigger_typing()
            await asyncio.sleep(0.5)
            await ctx.send("No results found, please try again")
            return


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
    if (randomNum % 2 == 0):
        # locate the specific keyword to associate the correct meme or gif
        if "chocolate" in arg:
            embedRecipe.set_image(url = "https://media3.giphy.com/media/JpehtCvclNLSE/giphy.gif?cid=790b76111a633b4e28035d07ecd58f69587130f7c54cf3e5&rid=giphy.gif&ct=g")
        elif "quinoa" in arg:
            embedRecipe.set_image(url = "https://i1.wp.com/i.giphy.com/media/8EpFqeoStLm4FLaWxC/giphy.gif")
        elif "flour" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/ab3DJeJOmJQAAAAd/cake-mistake.gif")
        elif "chicken" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/4kVtSIKi46YAAAAC/chicken-starbucks.gif")
        elif "broccoli" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/pfPkY9-DrEMAAAAC/broccoli-eat-me.gif")
        elif "potato" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/G24ZSNHLmRUAAAAC/yahia-potato.gif")
        elif "milk" in arg:
            embedRecipe.set_image(url = "https://c.tenor.com/9wGf-oOHKMsAAAAd/cow-cow-milk.gif")
            
    button_Ing = Button(label="Ingredients", style="2", custom_id="b1")
    button_Stop = Button(label="Stop", style="2", custom_id="b2")
    button_Ref = Button(label="Refresh", style="2", custom_id="b3")

    await ctx.trigger_typing()
    await asyncio.sleep(0.5)
    await ctx.send(embed=embedRecipe, components=[[button_Ing, button_Stop, button_Ref]])
    # storing ingredients and creating an embed to display to the user
    ingredients = scraper.ingredients()
    embedIngredients = discord.Embed(title='List of Ingredients', description="\n".join(ingredients), color=discord.Colour(0x3498DB))
    embedStop = discord.Embed()
    embedStop.set_image(url="https://c.tenor.com/okyDOdvpVDcAAAAC/master-chef-gordon-ramsey.gif")
    embed_no = discord.Embed(title="", description="")

    interaction = await bot.wait_for("button_click")
    if (interaction.component.custom_id == "b1"):
        await interaction.respond(embed=embedIngredients, ephemeral=False)
    elif (interaction.component.custom_id == "b2"):
        await interaction.respond(embed=embedStop, ephemeral=False)
    elif (interaction.component.custom_id == "b3"):
        await interaction.defer(ephemeral= False)
        await recipes(ctx = ctx, arg = arg)
        await interaction.respond(embed=embed_no)

    
    
# gathering what recipe our bot will search for
@bot.command(description='Call this command to search for recipes with certain ingredients')
# adding a cooldown between commands
@commands.cooldown(1, 5, commands.BucketType.user)
async def exclude(ctx, *, arg):
    

    # begins by getting access to the recipe site we want to use and searches by the users input

    # getting url of our current page, which is going to be the page where the recipes are
    url = 'https://www.allrecipes.com/search/results/?search=&IngExcl=' + arg.replace(" ", "&IngExcl=")

    # now creating variable r to get access to our url using BeautifulSoup
    r = requests.get(url)
    sourcePage = r.text

    soup = BeautifulSoup(sourcePage, 'lxml')

    # handling the cases where the users search might yield no results
    check_result = soup.findAll('div', {"class" : "searchResults__noResultsContainer"})
    for i in check_result:
        if (i.find('p').text.strip() == 'Check your spelling, try a more generic term, or less terms'):
            await ctx.trigger_typing()
            await asyncio.sleep(0.5)
            await ctx.send("No results found, please try again")
            return

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

    button_Ing = Button(label="Ingredients", style="2", custom_id="b1")
    button_Stop = Button(label="Stop", style="2", custom_id="b2")
    button_Ref = Button(label="Refresh", style="2", custom_id="b3")

    await ctx.trigger_typing()
    await asyncio.sleep(0.5)
    await ctx.send(embed=embedRecipe, components=[[button_Ing, button_Stop, button_Ref]])
    # storing ingredients and creating an embed to display to the user
    ingredients = scraper.ingredients()
    embedIngredients = discord.Embed(title='List of Ingredients', description="\n".join(ingredients), color=discord.Colour(0x3498DB))
    embedStop = discord.Embed()
    embedStop.set_image(url="https://c.tenor.com/okyDOdvpVDcAAAAC/master-chef-gordon-ramsey.gif")
    embed_no = discord.Embed(title="", description="")

    interaction = await bot.wait_for("button_click")
    if (interaction.component.custom_id == "b1"):
        await interaction.respond(embed=embedIngredients, ephemeral=False)
    elif (interaction.component.custom_id == "b2"):
        await interaction.respond(embed=embedStop, ephemeral=False)
    elif (interaction.component.custom_id == "b3"):
        await interaction.defer(ephemeral= False)
        await exclude(ctx = ctx, arg = arg)
        await interaction.respond(embed=embed_no)
    

    
# sort of overwriting help command to follow a certain format
@bot.command(description='Call this command to get a list of commands')
async def help(ctx):
  
    embed = discord.Embed(color=discord.Color.green(), title = "Commands supported by Recipe Bot")
    embed.add_field(name="!recipes", value="Search for recipes with specific keywords")
    embed.add_field(name="!ingredients", value="Search for recipes with ingredients on-hand")
    embed.add_field(name="!exclude", value="Search for recipes without certain ingredients")
    embed.add_field(name="!convert", value="Convert numbers from one unit of measurement to another")
    embed.add_field(name="!measurements", value ="Get a list of valid inputs for the !convert" )
    embed.add_field(name="!timer", value="Create a timer to keep track of your recipes")
    embed.add_field(name="!categories", value="Select a category of food from a dropdown menu")
    await ctx.send(embed=embed)

      
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

    # array with volumetric measurements
    vol = ['Teaspoons (tsp):          **teaspoon**',
               'Tablespoons (Tbsp):       **tablespoon**',
               'Gills (gi):               **gill**',
               'Imperial Gills (gi):      **UK+gill**',
               'Cups (c):                 **cup**',
               'Imperial Cups (c):        **UK+cup**',
               'Pints (pt):               **pint**',
               'Imperial Pints (pt):      **UK+pint**',
               'Imperial Quarts (qt):     **UK+quart**',
               'Gallons (gal):            **gal**',
               'Imperial Gallons (gal):   **UK+gal**']
    # array with weighted measurements
    weight = ['Ounces (oz):              **oz**',
              'Fluid Ounces (fl. oz.):   **fluid+oz**',
              'Grains (gr):              **grain**',
              'Grams (g):                **g**',
              'Decagrams (dag):          **decagram**',
              'Kilograms (kg):           **kg**',
              'Pounds (lb):              **lb**']
    # array with temperature measurements
    temp = ['Celsius (°C):             **c**',
            'Fahrenheit (°F):          **f**']

    embedUnits = discord.Embed(title = 'Supported Cooking Measurements', color = discord.Colour(0xDC143C))
    embedUnits.add_field(name = 'Volume Measurements', value = '\n'.join(vol))
    embedUnits.add_field(name = 'Weight Measurements', value = '\n'.join(weight))
    embedUnits.add_field(name = 'Weight Measurements', value = '\n'.join(temp))

    await ctx.send(embed = embedUnits)


#timer fucntion format: <Timer name> <minutes> <seconds>
@bot.command(description='A timer to help with tracking time')
async def timer(ctx,name:str,minutes:int,seconds=0):

    totalTime= ((minutes*60) + seconds)

    #time in seconds since Unix epoch
    currentTime = time.time()
    targetTime = totalTime + currentTime
   
    # no negative inputs
    if minutes <0 or seconds< 0:
        await ctx.send("number can't be a negative")
    else:
        #initial display
        embedVar1 = discord.Embed(title="Timer", description= f"Timer set by:{ctx.message.author.mention} ", color=0x336EFF)
        embedVar1.add_field(name=f"{name}",value = "timer name", inline=False)
        embedVar1.add_field(name=f"time set to:",value =  f"{minutes} minutes:{seconds} seconds", inline=False)
        embedVar1.add_field(name=f"Timer:{minutes}:{seconds}", value=f"{minutes}:{seconds}", inline=False)
    
        message1 = await ctx.send(embed = embedVar1)

        # loop used to display and edit timer in message
        while targetTime>currentTime:
            currentTime = time.time()

            #difference between times
            timeDifference = targetTime - currentTime

            #editing counter after each iteration.
            embedVar2 = discord.Embed(title=f"Timer for: {name}", description= f"Timer set by:{ctx.message.author.mention}", color=0x336EFF)
            embedVar2.add_field(name=f"Time set to:",value =  f"{minutes} minutes:{seconds} seconds", inline=False)
            embedVar2.add_field(name=f"Timer:", value=f"{int(timeDifference/60)}:{int(60*((timeDifference/60)-int(timeDifference/60)))}", inline=False)
            await message1.edit(embed = embedVar2)

        # making sure timer displays 0:0 when it terminates
        embedVar3 = discord.Embed(title=f"Timer for: {name}", description= f"Timer set by:{ctx.message.author.mention}", color=0x336EFF)
        embedVar3.add_field(name=f"Time set to:",value =  f"{minutes} minutes:{seconds} seconds", inline=False)
        embedVar3.add_field(name=f"Timer:", value="0:0", inline=False)
        await message1.edit(embed = embedVar3)

        embedVar = discord.Embed(title=f"Timer for {name} has ended", description= f"Timer set by:{ctx.message.author.mention}", color=0x336EFF)
        embedVar.set_image(url = 'https://c.tenor.com/zk8raXIIkcUAAAAC/gordon-ramsay-master-chef.gif')
        await ctx.send(embed=embedVar)

#method used to search recipes for a given category
def search(category):

    #categories urls (breakfast, lunch, dinner)
    lunch ='https://www.allrecipes.com/recipes/17561/lunch/'
    breakfast ='https://www.allrecipes.com/recipes/78/breakfast-and-brunch/'
    dinner = 'https://www.allrecipes.com/recipes/17562/dinner/'
    mexican = 'https://www.allrecipes.com/recipes/728/world-cuisine/latin-american/mexican/'
    chinese = 'https://www.allrecipes.com/recipes/695/world-cuisine/asian/chinese/'
    italian = 'https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/'
    lowcalorie = 'https://www.allrecipes.com/recipes/1232/healthy-recipes/low-calorie/'

    #getting driver according to category
    if category == "lunch":
        driver.get(lunch)
    elif category== "breakfast":
        driver.get(breakfast)
    elif category== "dinner":
        driver.get(dinner)
    elif category== "mexican":
        driver.get(mexican)
    elif category =="chinese":
        driver.get(chinese)
    elif category =="italian":
        driver.get(italian)
    elif category ==("lowCalorie"):
        driver.get(lowcalorie)
    # getting url of our current page, which is going to be the page where the recipes are
    url = driver.current_url
    
    # now creating variable r to get access to our url using BeautifulSoup 
    r = requests.get(url)
    sourcePage = r.content

    soup = BeautifulSoup(sourcePage, 'lxml')
    
    # going through web page to find all instances of a certain div
    random_link = soup.findAll('a', {"class" : "card__titleLink manual-link-behavior elementFont__titleLink margin-8-bottom"}, limit = 4)
    # grabbing a random link from our list to display to the user
    # this way they won't see duplicate results as often
    randomNum = random.randint(0, len(random_link)-1)
    #getting link from div
    link = random_link[randomNum].get('href')
        
    scraper = scrape_me(link)
        
    # getting access to our desired recipe page to scrape more information
    r = requests.get(link)
    sourcePage = r.content
    soup = BeautifulSoup(sourcePage, 'lxml')

    # scraping through the page to find a description
    desc = soup.find('p', {"class" : "margin-0-auto"})

    # sending a formatted message with the recipes title, description, link, and image
    embedRecipe = discord.Embed(title=scraper.title(), description="{}".format(desc.text), color=discord.Colour(0x8A2BE2), url = link)
    embedRecipe.set_image(url="{}".format(scraper.image()))

    return embedRecipe
    
@bot.command()
async def categories(ctx):

    #Drop down menu
    await ctx.send("categories",components=[
        Select(
            placeholder= "select a category", 
            options=[
                SelectOption(label= "Lunch",value = 'lunch'),
                SelectOption(label= "Breakfast",value = 'breakfast'),
                SelectOption(label= "Dinner",value = 'dinner'),
                SelectOption(label= "Mexican",value = 'mexican'),
                SelectOption(label= "Italian", value= 'italian'),
                SelectOption(label= "Chinese", value = 'chinese'),
                SelectOption(label= "Low-Calorie", value = 'lowCalorie'),
            ],custom_id="select1",
        )
            ],
                 )
   

#event created after selecting a category  
@bot.event
async def on_select_option(interaction):
    
   # provide more timer for interaction
    await interaction.defer(ephemeral= False)
    
    #searching for a recipe
    embed1 =search(interaction.values[0])
    
    await interaction.respond(embed = embed1)

    
bot.run('OTUyMjg0NjE1NTM0NTgzODA4.YizyKA.3fnwxAhIObzZBV_FZ04DsjwSgEM')
