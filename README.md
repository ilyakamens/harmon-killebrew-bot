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
- A local MySQL DB
- A file containing a JSON list of players in the room

## Usage
`python ~/path/to/bot.py <api_token> <room_id> <db_name> <user_list_file>`
