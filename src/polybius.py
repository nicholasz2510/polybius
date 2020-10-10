import discord
from discord.ext import commands
import json

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    global data
    data_file = open("../data.json")
    data = json.load(data_file)


@bot.command()
async def info(ctx):
    await ctx.send('TODO help')


@bot.command()
@commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
async def daily(ctx):
    await ctx.send('TODO daily')


f = open('../secret.txt', 'r')
bot.run(f.readline())
f.close()
