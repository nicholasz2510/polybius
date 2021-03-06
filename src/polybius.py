import asyncio
import discord
from discord.ext import commands
import json
import math
import datetime
import os
import random

trivia_answers = [":regional_indicator_a:", ":regional_indicator_b:", ":regional_indicator_c:", ":regional_indicator_d:"]
unicode_max_answers = ['🇦', '🇧', '🇨', '🇩']

bot = commands.Bot(command_prefix='$')

with open("../data.json") as data_file:
    data = json.load(data_file)


@bot.event
async def on_ready():
    print('Logged on as ' + str(bot.user))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That wasn't a valid command!\nType `$help` to see a list of commands.")
    else:
        raise error


@bot.command()
@commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
async def daily(ctx):
    discord_id = str(ctx.message.author.id)
    if discord_id not in data:
        await ctx.send("You need to register first! Do `$register`")
    else:
        data[discord_id]["points"] += 1
        await ctx.send("You got 1 :candy:")
        _save()


@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('You already claimed your daily reward! Try again in ' + str(datetime.timedelta(seconds=math.floor(error.retry_after))))
    else:
        raise error


@bot.command()
@commands.cooldown(1, 60 * 60 * 24 * 30, commands.BucketType.user)
async def monthly(ctx):
    discord_id = str(ctx.message.author.id)
    if discord_id not in data:
        await ctx.send("You need to register first! Do `$register`")
    else:
        data[discord_id]["points"] += 10
        await ctx.send("You got 1 :chocolate_bar: (equivalent to 10 :candy:)")
        _save()


@monthly.error
async def monthly_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('You already claimed your monthly reward! Try again in ' + str(datetime.timedelta(seconds=math.floor(error.retry_after))))
    else:
        raise error


@bot.command()
async def pot(ctx, recipient: discord.Member):
    if str(ctx.message.author.id) in data:
        if data[str(ctx.message.author.id)]["honey_potter"]:
            if not str(recipient.id) in data:
                await ctx.send("The person you're giving a :honey_pot: to hasn't registered yet! Tell them to do `$register`")
                return
            if ctx.message.author.id == recipient.id:
                await ctx.send("You can't pot yourself... :unamused:")
                return
            data[str(recipient.id)]["points"] += 100
            _save()
            await ctx.send("Wow! <@" + str(ctx.message.author.id) + "> just gave <@" + str(recipient.id) + "> a :honey_pot:! (worth 100 :candy:)")
        else:
            await ctx.send("Hey, you don't have permission to do that!")
    else:
        await ctx.send("You need to register first! Do `$register`")


@pot.error
async def pot_error(ctx, error):
    await ctx.send('Make sure you have the recipient in the command: `$pot <recipient>`')


@bot.command()
async def trivia(ctx):
    discord_id = str(ctx.message.author.id)
    if discord_id not in data:
        await ctx.send("You need to register first! Do `$register`")
        return

    with open("../trivia/" + random.choice(os.listdir("../trivia")), encoding="utf-8") as trivia_file:
        trivia_questions = json.load(trivia_file)
    question = trivia_questions[random.randint(0, len(trivia_questions) - 1)]
    message = "Question for <@" + str(ctx.message.author.id) + ">:\n" + question["question"] + "\n\n"
    unicode_answers = unicode_max_answers[:len(question["choices"])]
    answer = question["choices"].index(question["answer"])
    for i in range(len(question["choices"])):
        message += trivia_answers[i] + " " + question["choices"][i] + "\n"
    sent = await ctx.send(message)
    for c in unicode_answers:
        await sent.add_reaction(c)

    print(trivia_answers[answer] + " " + question["answer"])

    def check(reaction_arg, user_arg):
        return user_arg == ctx.message.author

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Trivia question for <@" + str(ctx.message.author.id) + "> timed out.")
        return

    if unicode_answers.index(str(reaction)) == answer:
        data[discord_id]["points"] += 5
        await ctx.send("<@" + str(ctx.message.author.id) + "> " + trivia_answers[answer] + " " + question["answer"] + " was correct! You received 1 :lollipop: (equivalent to 5 :candy:)")
        _save()
    else:
        data[discord_id]["points"] -= 1
        await ctx.send("<@" + str(ctx.message.author.id) + "> " + str(reaction) + " " + question["choices"][unicode_answers.index(str(reaction))] + " was incorrect... The correct answer was " + trivia_answers[answer] + " " + question["answer"] + ". You lost 1 :candy:")
        _save()


@bot.command()
async def bal(ctx):
    discord_id = str(ctx.message.author.id)
    if discord_id in data:
        await ctx.send("You have " + str(data[discord_id]["points"]) + " :candy:")
    else:
        await ctx.send("You need to register first! Do `$register`")


@bot.command()
async def register(ctx):
    discord_id = str(ctx.message.author.id)
    if discord_id not in data:
        data[discord_id] = {}
        data[discord_id]["points"] = 0
        data[discord_id]["honey_potter"] = False
        await ctx.send("You've been registered!")
        _save()
        daily.reset_cooldown(ctx)
        monthly.reset_cooldown(ctx)
    else:
        await ctx.send("You are already registered!")


def _save():
    with open('../data.json', 'w+') as file_save:
        json.dump(data, file_save)


with open('../secret.txt', 'r') as f:
    bot.run(f.readline())
