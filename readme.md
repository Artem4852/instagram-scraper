# Instagram Scraper

This project provides a Python-based Instagram scraper that allows you to download user information, posts, followers, following, stories, and highlights from public Instagram profiles.

## Table of Contents

- [Setup](#setup)
- [For Users](#for-users)
- [For Developers](#for-developers)
- [Folder Structure](#folder-structure)

## Setup

1. Clone this repository to your local machine.
2. Install the required dependencies:
   ```
   pip install python-dotenv requests rocketapi
   ```
3. Create a `.env` file in the root directory of the project.
4. Add your RocketAPI token(s) to the `.env` file:
   ```
   tokens=your_token_1,your_token_2,your_token_3
   ```
   Note: You can get a trial token for 100 requests at [https://rocketapi.io/](https://rocketapi.io/)

## For Users

Users can interact with the scraper through a command-line interface provided in `main.py`. This script offers a menu-driven approach to scraping Instagram data.

### How to Use

1. Run the script:
   ```
   python main.py
   ```
2. Enter the Instagram username you want to scrape when prompted.
3. Choose from the following options:
   1. Download user's info
   2. Download user's posts
   3. Download user's followers
   4. Download user's following
   5. Download user's stories
   6. Download user's highlights
   7. Exit

For options 2-6, you'll be asked if you want to update existing data and, for some options, you can specify a limit on the number of items to download.

Note: If the user's profile is private, you'll only be able to download their public information.

## For Developers

Developers can utilize the `UserScraper` class from `api.py` to integrate Instagram scraping functionality into their own projects.

### Class: UserScraper

#### Initialization

```python
from api import UserScraper

scraper = UserScraper(username, save=True, debug=False, parent_path=None)
```

- `username`: Instagram username or user ID
- `save`: Whether to save data to disk (default: True)
- `debug`: Whether to print debug messages (default: False)
- `parent_path`: Path to save the data (default: current directory)

#### Methods

- `download_user_info(user_info=None, update=False)`: Download user's basic information
- `get_user_posts(limit=None, update=False)`: Get user's posts
- `download_user_posts(posts=None, limit=None, update=False)`: Download user's posts
- `get_user_stories()`: Get user's current stories
- `download_user_stories(stories=None)`: Download user's current stories
- `get_user_highlights(update=False)`: Get user's highlights
- `download_user_highlights(highlights=None, update=False)`: Download user's highlights
- `get_user_followers(limit=None, update=False)`: Get user's followers
- `download_user_followers(followers=None, limit=None, update=False)`: Download user's followers
- `get_user_following(limit=None, update=False)`: Get user's following
- `download_user_following(following=None, limit=None, update=False)`: Download user's following

### Example Usage

```python
from api import UserScraper

# Initialize the scraper
scraper = UserScraper('instagram', debug=True)

# Download user info
scraper.download_user_info()

# Download the first 50 posts
scraper.download_user_posts(limit=50)

# Download all followers
scraper.download_user_followers()
```

Remember to handle potential exceptions, such as `NotFoundException` when a user doesn't exist.

## Folder Structure

The Instagram scraper creates a folder structure to organize the downloaded data. Here's an overview of the folder structure created for each scraped user:

```
[username]/
├── raw/
│   ├── basic_user_info_[timestamp].json
│   ├── user_info_[timestamp].json
│   ├── stories_[timestamp].json
│   ├── posts/
│   │   ├── posts_0_[timestamp].json
│   │   ├── posts_1_[timestamp].json
│   │   └── ...
│   ├── highlights_[timestamp].json
│   ├── highlights/
│   │   ├── [title1]_[timestamp].json
│   │   ├── [title2]_[timestamp].json
│   │   └── ...
│   ├── followers/
│   |   ├── followers_0_[timestamp].json
│   |   ├── followers_1_[timestamp].json
│   |   └── ...
│   ├── following/
│   |   ├── following_0_[timestamp].json
│   |   ├── following_1_[timestamp].json
│   └── ...
├── posts/
│   ├── post_[date]/
│   │   ├── 0.jpg
│   │   ├── 1.mp4
│   │   ├── ...
│   │   ├── caption.txt
│   │   └── data_[timestamp].json
│   └── ...
├── stories/
│   ├── story_[date].jpg
│   ├── story_[date].mp4
│   ├── story_[date]_[timestamp].json
│   └── ...
├── highlights/
│   ├── [highlight_title]/
│   │   ├── story_[date].jpg
│   │   ├── story_[date].mp4
│   │   ├── ...
│   │   └── data_[timestamp].json
│   └── ...
├── followers/
│   ├── followers_full_[timestamp].json
│   └── followers_short_[timestamp].json
├── following/
│   ├── following_full_[timestamp].json
│   └── following_short_[timestamp].json
├── user_info_[timestamp].json
├── user_info.txt
├── propic.jpg
└── loaded.json
```

- `raw/`: Contains the raw JSON responses from the API for various requests.
- `posts/`: Each post is stored in a separate folder named with the post's date. It contains media files, caption, and some of the post's data.
- `stories/`: Contains the user's stories, named with the story's date and stories' data.
- `highlights/`: Each highlight is stored in a separate folder, containing its stories and data.
- `followers/` and `following/`: Contains JSON files with the user's followers and following lists.
- `user_info_[timestamp].json`: A JSON file containing basic user information.
- `propic.jpg`: The user's profile picture.
- `loaded.json`: A JSON file keeping track of which media has been downloaded to avoid duplicates.

This structure allows for easy navigation and management of the scraped data.

## Notes

- Please respect users' privacy when using this scraper.
- The scraper's functionality depends on the RocketAPI service. Make sure you have valid tokens and haven't exceeded your request limit.
- For large-scale scraping, consider implementing rate limiting and error handling to avoid potential issues with the API.
