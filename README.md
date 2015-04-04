# harmon-killebrew-bot
A simple bot for playing [Harmon Killebrew (the celebrity name game)](https://localwiki.org/davis/Harmon_Killebrew) in HipChat

# Description
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
- populating config.json with real data

## Installation
1. `git clone git@github.com:ilyakamens/harmon-killebrew-bot.git`
2. put real data into config.json
3. `cd harmon-killebrew-bot`
4. `sudo ./install.sh`

## Usage
`python bot.py`
