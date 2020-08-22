A Discord bot that gives trivia to users, using discord.py

**Instructions**  
Add Discord bot token in placeholder in .env

Add Discord user ID's of guild members who are able to shut down bot with !disconnect in developers_id_list.txt

In terminal, run this command:  
`python TriviaBot.py`

**Dependencies**    
`discord.py`  
`dotenv`  
`asyncio`  
`pandas`  
`os`  
`json`  
`random`  
`shutil`  

**Files**  
1. `TriviaBot.py`: main code that uses concurrent programming with `discord.py` to listen and respond to commands  
2. `manage_questions.py`: contains the `Questions` class that imports questions, returns individual questions, and save question order on disconnect  
3. `trivia_questions_guild_*.csv`: contains last saved list of questions for a guild  
4. `bot_responses.json`: contains responses that bot could use for different situations
5. `current_state.json`: contains current question, answer, category, and scores for players. Using a dictionary allows bot to retrieve scores by looking up the guild ID then member ID in constant time