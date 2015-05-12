# harmon-killebrew-bot
A simple bot for playing <a href="https://localwiki.org/davis/Harmon_Killebrew" target="_blank">Harmon Killebrew (the celebrity name game)</a> in <a href="https://www.hipchat.com/" target="_blank">HipChat</a>

## Description
- harmon-killebrew-bot will listen to HipChat messages and write celebrity names to a MySQL DB
- it will reject previously used submissions
- it will choose the next person in the list and @mention them
- it recognizes same first-letter names and will reverse the order
- it currently stores the celebrity name, as well as the author and date of the submission

## Requirements
- <a href="https://github.com/PyMySQL/PyMySQL" target="_blank">PyMySql</a>
- <a href="https://github.com/a2design-inc/hipster" target="_blank">Hipster</a>
- <a href="https://www.mysql.com/" target="_blank">MySQL</a>
- <a href="http://mysql-python.sourceforge.net/" target="_blank">MySQLdb</a>
- populating `config.json` with real data

## Installation (Ubuntu)
1. `git clone git@github.com:ilyakamens/harmon-killebrew-bot.git`
2. put real data into config.json
3. `cd harmon-killebrew-bot`
4. `sudo ./install.sh`

## Usage
`python bot.py`

## Super user commands
`config.json` specifies a super user, who has two commands at his/her disposal when written into the chat:
- `reverse order` (switches the order the bot chooses players in)
- `set current player: full_name` (sets full_name [e.g. Ilya Kamens] to be the current player)
- `set current letter: some_letter` (sets current letter to some_letter)
- `who's next` (makes bot say who the next player is)
- `(downvote) submission` (removes submission from the mysql table and sets current player to whomever authored the submission)
- `who's current` (makes bot say who the current player is)
- `skip` skips current player

## Retroactive importing
Maybe you've been playing this game for a bit and want an easy way to add a list of names to the DB that have already been used. No problem:
- create a file with one name per line (e.g. `names.txt`)
- `python import.py names.txt`
- if you do this, know that the `author` will be `IMPORT` and `authored` will be the current date
