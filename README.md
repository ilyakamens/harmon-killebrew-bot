# harmon-killebrew-bot
A simple bot for playing [Harmon Killebrew (the celebrity name game)](https://localwiki.org/davis/Harmon_Killebrew) in HipChat

## Description
- harmon-killebrew-bot will listen to HipChat messages and write celebrity names to a MySQL DB
- it will reject previously used submissions
- it will choose the next person in the list and @mention them
- it recognizes same first-letter names and will reverse the order
- it currently stores the celebrity name, as well as the author and date of the submission

## Requirements
- [PyMySql](https://github.com/PyMySQL/PyMySQL)
- [Hipster](https://github.com/a2design-inc/hipster)
- MySQL
- MySQLdb
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

## Reotractive importing
Maybe you've been playing this game for a bit and want an easy way to add a list of names to the DB that have already been used. No problem:
- create a file with one name per line (e.g. `names.txt`)
- `python import.py names.txt`
- if you do this, know that the `author` will be `IMPORT` and `authored` will be the current date
