#TriviaBot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import manage_questions as mq
import json
import random

debugging = True

### INITIAL SET UP ###
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

QUESTIONS = {} #dictionary containing a question object for each guild
CATEGORIES = {} #dictionary containing a list of question categories for each guild
#dictionary containing current question, answer, category, and scores for each member
with open('current_state.json', 'r') as cs_file:
    CURRENT_STATE = json.load(cs_file)
#dictionary containing several different reponses bot could use
with open('bot_responses.json', 'r') as br_file:
    BOT_REPONSES = json.load(br_file)

# decorator to call bot.command method using on_ready as a parameter
# defines a new method that is the same as the function below
@bot.event
async def on_ready():
    global QUESTIONS, CATEGORIES
    print(f'{bot.user} has connected to Discord.')
    #initialize global variables
    for guild in bot.guilds:
        q_object = mq.Questions('trivia_questions_guild_' + str(guild.id) + '.csv')
        QUESTIONS.update({str(guild.id) : q_object})
        CATEGORIES.update({str(guild.id) : q_object.get_categories()})
        await update_guilds_dict(guild) #ensure all guilds are in CURRENT_STATE
        for member in guild.members: #ensure all members of guild are in CURRENT_STATE
            await update_members_dict(member)
        

@bot.event
async def on_member_join(member):
    #ignores bots
    if not member.bot:
        await update_members_dict(member)

@bot.command(help='!yeet <object>')
async def yeet(ctx, *args):
    if args:
        response = 'TriviaBot YEETS ' + ' '.join(args)
    else:
        response = 'YEEEEEEEEEEEEEEEEEEET'
    await ctx.send(response)

### QUESTIONS AND ANSWER FUNCTIONS ###
@bot.command(name='categories', help = 'give categories of questions')
async def give_categories(ctx):
    response = []
    for index, value in enumerate(CATEGORIES[str(ctx.guild.id)]):
        response.append(str(index) + '  ' + value)
    await ctx.send('\n'.join(response))

question_help = '!q gives a random trivia question, !q <category> gives a question in <category>'
@bot.command(name='q', help = question_help)
async def give_question(ctx, *category): #category will always be tuple
    global CATEGORIES, CURRENT_STATE

    valid_input = False
    if category: #if category parameter exists
        if category[0].isdigit() and (0 < int(category[0]) < len(CATEGORIES[str(ctx.guild.id)])): #if input is an int
            input_cat = CATEGORIES[str(ctx.guild.id)][int(category[0])]
        elif len(category) == 1: #if input is a single word
            input_cat = category[0]
        elif len(category) > 1: #if input is multiple words
            input_cat = ' '.join(category)
        try:
            qsn, ans, returned_cat = QUESTIONS[str(ctx.guild.id)].get_question(input_cat)
            CURRENT_STATE[str(ctx.guild.id)]['question'] = qsn #update current qsn, ans, and cat
            CURRENT_STATE[str(ctx.guild.id)]['answer'] = (ans, False) #False = user input is not the correct answer
            CURRENT_STATE[str(ctx.guild.id)]['category'] = returned_cat
            valid_input = True
        except UnboundLocalError:
            await ctx.send('that category does not exist')
    else:
        qsn, ans, returned_cat = QUESTIONS[str(ctx.guild.id)].get_question()
        CURRENT_STATE[str(ctx.guild.id)]['question'] = qsn
        CURRENT_STATE[str(ctx.guild.id)]['answer'] = (ans, False)
        CURRENT_STATE[str(ctx.guild.id)]['category'] = returned_cat
        valid_input = True
    
    if valid_input:
        if debugging:
            print('Current question: ',qsn)
            print('Current answer: ',ans)
        
        await ctx.send('Category: ' + returned_cat + '\n' + 'Question: ' + qsn)
    
@bot.command(name='a', help = '!a <answer> to answer the question')
async def give_answer(ctx, *input_answer):
    global CURRENT_STATE
    
    if input_answer:
        (ans, ans_flag) = CURRENT_STATE[str(ctx.guild.id)]['answer'] #current correct answer
        if ans.lower() == ' '.join(input_answer).lower() and ans_flag == False:
            await ctx.send(random.choice(BOT_REPONSES['correct answer']))
            await award_points(ctx, 1)
            ans_flag = True
        elif ans_flag == True: #if question is already answered correctly
            await ctx.send(random.choice(BOT_REPONSES['already answered']))
        elif ans.lower() != ' '.join(input_answer).lower() and ans_flag == False:
            await ctx.send(random.choice(BOT_REPONSES['incorrect answer']))
        CURRENT_STATE[str(ctx.guild.id)]['answer'] = (ans, ans_flag) #update current answer and flag

@bot.command(help = 'return current scores')
async def scores(ctx):
    response = '☜(ﾟヮﾟ☜) ***Scores for ' + str(ctx.message.author.name) + '*** (☞ﾟヮﾟ)☞\n'
    dict_str = print_dict(CURRENT_STATE[str(ctx.guild.id)][str(ctx.message.author.id)])
    await ctx.send(response + dict_str)

@bot.command(name = 'giveup', help = '!giveup: returns answer')
async def give_up(ctx):
    (ans, ans_flag) = CURRENT_STATE[str(ctx.guild.id)]['answer'] 
    if ans_flag == True:
        await ctx.send(random.choice(BOT_REPONSES['give up answered']))
    else:
        await ctx.send(random.choice(BOT_REPONSES['give up not answered']) + 'the correct answer is: ' + str(ans))

@bot.command(help='terminates bot')
async def disconnect(ctx):
    with open('developers_id_list.txt', 'r') as dev_id_file:
        dev_ids = [int(line.rstrip()) for line in dev_id_file.readlines()]
        if ctx.message.author.id in dev_ids: #dc if message sender is a dev
            for guild in bot.guilds: #save current question order
                QUESTIONS[str(guild.id)].save_questions_state('trivia_questions_guild_' + str(guild.id) + '.csv')
            with open('current_state.json', 'w') as f: #save current state
                json.dump(CURRENT_STATE, f)
            await ctx.send(random.choice(BOT_REPONSES['dev dc']))
            await bot.logout()
        else:
            await ctx.send(random.choice(BOT_REPONSES['non-dev dc']))

### HELPER FUNCTIONS ###
async def add_new_category_score(ctx, category): #keeps track of scores for new category
    global CURRENT_STATE
    for member in ctx.message.guild.members:
        CURRENT_STATE[str(ctx.guild.id)][str(member.id)].update({category:0})

async def update_members_dict(member):
    global CURRENT_STATE, CATEGORIES
    if not str(member.id) in CURRENT_STATE[str(member.guild.id)]: #if member is not stored in current state
        CURRENT_STATE[str(member.guild.id)][str(member.id)] = {'single-player score' : 0}
        CURRENT_STATE[str(member.guild.id)][str(member.id)].update({cat:0 for cat in CATEGORIES[str(member.guild.id)]})

async def update_guilds_dict(guild):
    global CURRENT_STATE, CATEGORIES
    if not str(guild.id) in CURRENT_STATE: #if guild is not in current state
        # if debugging:
        #     print(guild.id)
        #     print(CURRENT_STATE.keys())
        init = {'question' : None, 'answer' : (None, False), 'category' : None}
        CURRENT_STATE.update({str(guild.id) : init})
    

async def award_points(ctx, points):
    global CURRENT_STATE
    category = CURRENT_STATE[str(ctx.guild.id)]['category'] #get category to award points for
    #if new category of questions is detected
    if not category in CURRENT_STATE[str(ctx.guild.id)][str(ctx.message.author.id)]:
        await add_new_category_score(ctx, category)
    CURRENT_STATE[str(ctx.guild.id)][str(ctx.message.author.id)][category] += points
    CURRENT_STATE[str(ctx.guild.id)][str(ctx.message.author.id)]['single-player score'] += points

def print_dict(dictionary):
    #returns the dictionary as a string, each key/value pair separated by newline
    result = ['💪 single-player score: ' + str(dictionary['single-player score'])]
    i = 0
    for key in sorted(dictionary):
        if key != 'single-player score':
            result.append(f'{i:02d}. ' + str(key) + ': ' + str(dictionary[key]))
            i += 1
    return '\n'.join(result)

bot.run(TOKEN)