from api import UserScraper
from rocketapi.exceptions import NotFoundException
import os

commands = """
Commands:
    1. Download user's info
    2. Download user's posts
    3. Download user's followers
    4. Download user's following
    5. Download user's stories
    6. Download user's highlights
    7. Exit
"""

username = input("Enter the username: ")
try: user = UserScraper(username)
except NotFoundException: 
    print("Can't find user with that username")
    os.system(f"rm -rf {username}")
    exit()
while True:
    os.system("clear")
    print("Done!")
    print(commands)
    command = input("Enter the command: ")
    if command != "7": update = input("Update data? (y/n): ") == "y"
    if command == "1":
        user.download_user_info(update=update)
    elif command == "7":
        break
    elif user.is_private:
        print("This user is private. You can't download posts, followers, following, stories and highlights")
    elif command == "2":
        limit = input("Enter the limit or leave empty to download all: ")
        if limit: limit = int(limit)
        user.download_user_posts(limit=limit, update=update)
    elif command == "3":
        limit = input("Enter the limit or leave empty to download all: ")
        if limit: limit = int(limit)
        user.download_user_followers(limit=limit, update=update)
    elif command == "4":
        limit = input("Enter the limit or leave empty to download all: ")
        if limit: limit = int(limit)
        user.download_user_following(limit, update=update)
    elif command == "5":
        user.download_user_stories()
    elif command == "6":
        user.download_user_highlights(update=update)
    else:
        print("Invalid command")