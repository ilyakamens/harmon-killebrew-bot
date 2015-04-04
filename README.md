# harmon-killebrew-bot
A simple bot for playing [Harmon Killebrew (the celebrity name game)](https://localwiki.org/davis/Harmon_Killebrew) in HipChat

# Description
- harmon-killebrew-bot will listen to HipChat messages and write celebrity names to a MySQL DB
- it will reject previously used submissions
- it will choose the next person in the list and @mention them
- it recognizes same first-letter names and will reverse the order
- it currently stores the celebrity name, who the celebrity was said by, and the date it was said

## Requirements
- [PyMySql](https://github.com/PyMySQL/PyMySQL)
- [Hipster](https://github.com/a2design-inc/hipster)
- MySQL
- A JSON config

## Usage
`python ~/path/to/bot.py <config_file.json>`
