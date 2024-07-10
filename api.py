from datetime import datetime
import os
import random
import json
import dotenv
import requests
from rocketapi import InstagramAPI

dotenv.load_dotenv()

tokens = str(os.getenv('tokens')).split(',')

class UserScraper():
    """
    Class to scrape Instagram data of a certain user
    
    Parameters:
    user (str): Username or user ID of the user to scrape
    save (bool): Whether to save the data to disk
    debug (bool): Whether to print debug messages
    parent_path (str): Path to save the data to. If not provided, saves to current directory"""
    def __init__(self, user: str | int, save=True, debug=False, parent_path=None) -> None:
        # Creating multiple API instances to avoid rate limits
        self.tokens = tokens
        self.apis = [InstagramAPI(token) for token in self.tokens]

        # Setting up the scraper
        self.parent_path = parent_path if parent_path else "."
        self.save = save
        self.debug = debug

        # Getting user ID and username
        if type(user) == str and not user.isdigit():
            self.username = user
            self.setup_directories()
            self.user_id = self.get_user_id(self.username)
        else:
            self.user_id = int(user)
            self.username = self.get_username(self.user_id)
            self.setup_directories()

        # Additional setup
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        self.loaded = self.load_loaded()

    def random_api(self) -> InstagramAPI:
        """
        Return a random API instance to avoid rate limits"""
        return random.choice(self.apis)

    def load_loaded(self) -> dict:
        """
        Load the data that was already loaded to avoid loading the same images/videos multiple 
        times"""
        if not os.path.exists(f'{self.parent_path}/{self.username}/loaded.json'): 
            return {'posts': [], 'stories': [], 'highlights': []}
        with open(f'{self.parent_path}/{self.username}/loaded.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_loaded(self) -> None:
        """
        Save the data that was already loaded to avoid loading the same images/videos multiple 
        times"""
        with open(f'{self.parent_path}/{self.username}/loaded.json', 'w', encoding='utf-8') as f:
            json.dump(self.loaded, f)

    def setup_directories(self) -> None:
        """
        Setup directories for the user. Creates directories for posts, stories, and highlights."""
        os.makedirs(f'{self.parent_path}/{self.username}', exist_ok=True)
        os.makedirs(f'{self.parent_path}/{self.username}/raw', exist_ok=True)
        os.makedirs(f'{self.parent_path}/{self.username}/posts', exist_ok=True)
        os.makedirs(f'{self.parent_path}/{self.username}/stories', exist_ok=True)
        os.makedirs(f'{self.parent_path}/{self.username}/highlights', exist_ok=True)
        os.makedirs(f'{self.parent_path}/{self.username}/followers', exist_ok=True)
        os.makedirs(f'{self.parent_path}/{self.username}/following', exist_ok=True)

    def save_json(self, data: dict, filename: str) -> None:
        """
        Save JSON data to a file
        
        Parameters:
        data (dict): Data to save
        filename (str): Name of the file to save the data to"""
        now = datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss')
        parent_path = os.path.dirname(f"{self.parent_path}/{self.username}/{filename}")
        os.makedirs(parent_path, exist_ok=True)
        with open(f"{self.parent_path}/{self.username}/{filename}_{now}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def find_latest_json(self, filename: str) -> str | None:
        """
        Find the latest JSON file in a directory
        
        Parameters:
        filename (str): Name of the file to search for"""
        files = os.listdir(f"{self.parent_path}/{self.username}/{'/'.join(filename.split('/')[:-1])}")
        files = [f for f in files if f.startswith(filename.split('/')[-1])]
        files.sort()
        if not files: return None
        if len(filename.split('/')) == 1: return files[-1].replace('.json', '')
        return os.path.join(*filename.split('/')[:-1], files[-1]).replace('.json', '')

    def load_json(self, filename: str) -> dict:
        """
        Load JSON data from a file"""
        with open(f"{self.parent_path}/{self.username}/{self.find_latest_json(filename)}.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def download_media(self, url: str, filename: str) -> None:
        """
        Download media from a URL
        
        Parameters:
        url (str): URL of the media
        filename (str): Name of the file to save the media to"""
        r = requests.get(url, headers=self.headers, timeout=1000)
        with open(f"{self.parent_path}/{self.username}/{filename}", 'wb') as f:
            f.write(r.content)

    def data_exists(self, filename) -> bool:
        """
        Check if data exists on disk
        
        Parameters:
        filename (str): Name of the file to check"""
        directory = f"{self.parent_path}/{self.username}/{'/'.join(filename.split('/')[:-1])}"
        if not os.path.exists(directory): 
            os.makedirs(directory, exist_ok=True)
            return False
        files = os.listdir(directory)
        files = [f for f in files if f.startswith(filename.split('/')[-1])]
        return any(files)

    def add_directory(self, path) -> None:
        """
        Creates a new directory in the parent path
        
        Parameters:
        path (str): Path to add"""
        os.makedirs(f"{self.parent_path}/{self.username}/{path}", exist_ok=True)

    def get_data(self, filename: str, update: bool, method: str, *args, **kwargs) -> dict:
        filename = 'raw/'+filename
        if update or not self.data_exists(filename):
            data = getattr(self.random_api(), method)(*args, **kwargs)
            if self.save:
                self.save_json(data, filename)
        else:
            data = self.load_json(filename)
        return data

    def get_user_id(self, username: str, update=False) -> int:
        """
        Get the user ID of a user by their username
        
        Parameters:
        username (str): Username of the user
        update (bool): Whether to update the data if it already exists. If False, loads the data 
        from disk"""

        if self.debug: 
            print(f"Getting user ID for {username}")
        filename = 'basic_user_info'

        # Getting data - either from API or from disk
        data = self.get_data(filename, update, 'get_user_info', username)
        return int(data['data']['user']['id'])

    def get_username(self, user_id: int) -> str:
        """
        Get the username of a user by their user ID
        
        Parameters:
        user_id (int): User ID of the user"""

        if self.debug:
            print(f"Getting username for user with id {user_id}")

        data = self.random_api().get_user_info_by_id(user_id)

        self.username = data['user']['username']

        return data['user']['username']

    def get_user_info(self, user_id: int, update=False) -> dict:
        """
        Get the user info of a user by their user ID
        
        Parameters:
        user_id (int): User ID of the user
        update (bool): Whether to update the data if it already exists. If False, loads 
        the data from disk"""

        if self.debug:
            print(f"Getting user info for user {self.username}")

        filename = 'user_info'
        data = self.get_data(filename, update, 'get_user_info_by_id', user_id)
        return data['user']

    def download_user_info(self, user_info=None, update=False) -> None:
        """
        Download user info to disk
        
        Parameters:
        user_info (dict): User info data. If not provided, gets the data from the API
        update (bool): Whether to update the data if it already exists. If False, loads 
        the data from disk"""

        if self.debug:
            print(f"Downloading user info for user {self.username}")

        # Getting user info from API if not provided
        if not user_info:
            user_info = self.get_user_info(self.user_id, update=update)

        # Writing basic user info to a file
        with open(f'{self.parent_path}/{self.username}/user_info.txt', "w", encoding='utf-8') as f:
            f.write(f"Username: {user_info['username']}\n")
            f.write(f"User ID: {user_info['pk']}\n")
            f.write(f"Full Name: {user_info['full_name']}\n")
            f.write(f"Biography: {user_info['biography']}\n")
            f.write(f"Followers: {user_info['follower_count']}\n")
            f.write(f"Following: {user_info['following_count']}\n")
            f.write(f"Posts: {user_info['media_count']}\n")

        self.save_json({
            'username': user_info['username'],
            'user_id': user_info['pk'],
            'full_name': user_info['full_name'],
            'biography': user_info['biography'],
            'followers': user_info['follower_count'],
            'following': user_info['following_count'],
            'posts': user_info['media_count']
        }, 'user_info')

        # Saving profile picture
        self.download_media(user_info['hd_profile_pic_url_info']['url'], 'propic.jpg')

    def get_user_posts(self, limit=None, update=False) -> list:
        """
        Get user posts
        
        Parameters:
        limit (int): Maximum number of posts to get. If not provided, gets all posts
        update (bool): Whether to update the data if it already exists. If False, loads 
        the data from disk"""

        if self.debug:
            print(f"Getting user posts for user {self.username}")

        # Setting limit to a high number if not provided
        if not limit:
            limit = 999999

        # Loading data for the first page from the API or from disk
        filename = 'posts/posts_0'
        data = self.get_data(filename, update, 'get_user_media', self.user_id, 50)

        posts = data['items']

        # Getting all the other posts
        page = 1
        while data['more_available'] and len(posts) < limit:
            # Loading data for the next page from the API or from disk
            filename = f'posts/posts_{page}'
            data = self.get_data(filename, update, 'get_user_media', self.user_id, 50, data['next_max_id'])
            posts += data['items']
            page += 1
        return posts

    def download_user_posts(self, posts=None, limit=None, update=False) -> None:
        """
        Download user posts to disk
        
        Parameters:
        posts (list): User posts data. If not provided, gets the data from the API
        limit (int): Maximum number of posts to download. If not provided, downloads all posts
        update (bool): Whether to update the data if it already exists. If False, loads 
        the data from disk"""

        # Getting user posts if not provided
        if not posts:
            posts = self.get_user_posts(limit, update=update)

        if self.debug:
            print(f"Downloading user posts for user {self.username}")

        if not limit:
            limit = 999_999_999_999

        # Downloading every post
        for n, post in enumerate(posts):
            if n >= limit:
                break
            date = datetime.fromtimestamp(post['taken_at']).strftime('%Y-%m-%d %Hh%Mm%Ss')
            self.add_directory(f'posts/post_{date}')
            if self.save and not self.data_exists(f'posts/post_{date}/data'):
                self.save_json({'data': post}, f'posts/post_{date}/data')

            # Loading every image/video in the post
            if 'carousel_media' in post:
                images = [im for im in post['carousel_media']]
            else: images = [post]
            for i, image in enumerate(images):
                # Skipping if the media was already loaded
                if image['id'] in self.loaded['posts']:
                    continue
                if 'video_versions' in image:
                    self.download_media(image['video_versions'][0]['url'], f'posts/post_{date}/{i}.mp4')
                else:
                    self.download_media(image['image_versions2']['candidates'][0]['url'], f'posts/post_{date}/{i}.jpg')

                # Adding the media to the loaded list
                self.loaded['posts'].append(image['id'])
                self.save_loaded()

            if not update: continue

            # Saving additional data
            self.save_json({
                'taken_at': post['taken_at'],
                'id': post['id'],
                'caption': post['caption']['text'] if 'caption' in post and 'text' in post['caption'] else None,
                'like_count': post['like_count'],
                'reshare_count': post['comment_count'],
                'comment_count': post['comment_count'],
                'media_count': len(images),
                'media_type': 'carousel' if 'carousel_media' in post else 'video' if 'video_versions' in post else 'photo'
            }, f'posts/post_{date}/data')

            # Loading the caption if it exists
            if not 'caption' in post:
                continue
            if not post['caption']:
                continue
            if not 'text' in post['caption']:
                continue
            with open(f'{self.parent_path}/{self.username}/posts/post_{date}/caption.txt', 'w', encoding='utf-8') as f:
                f.write(post['caption']['text'])

    def get_user_stories(self) -> list:
        """
        Get user stories"""

        if self.debug:
            print(f"Getting user stories for user {self.username}")

        # Getting stories data from the API
        data = self.random_api().get_user_stories(self.user_id)
        self.save_json(data, 'raw/stories')
        return data['reels'][str(self.user_id)]['items']

    def download_user_stories(self, stories=None) -> None:
        """
        Download user stories to disk
        
        Parameters:
        stories (list): User stories data. If not provided, gets the data from the API"""

        # Getting user stories if not provided
        if not stories:
            stories = self.get_user_stories()

        if self.debug:
            print(f"Downloading user stories for user {self.username}")

        for story in stories:
            # Skipping if the story was already loaded
            if story['id'] in self.loaded['stories']:
                continue

            date = datetime.fromtimestamp(story['taken_at']).strftime('%Y-%m-%d %Hh%Mm%Ss')

            self.save_json({
                'taken_at': story['taken_at'],
                'id': story['id'],
                'media_type': 'video' if 'video_versions' in story else 'photo'
            }, f'stories/story_{date}')

            # Downloading the story
            if 'video_versions' in story:
                self.download_media(story['video_versions'][0]['url'], f'stories/story_{date}.mp4')
            else:
                self.download_media(story['image_versions2']['candidates'][0]['url'], f'stories/story_{date}.jpg')

            # Adding the story to the loaded list
            self.loaded['stories'].append(story['id'])
            self.save_loaded()

    def get_user_highlights(self, update=False) -> list:
        """
        Get user highlights
        
        Parameters:
        update (bool): Whether to update the data if it already exists. If False, 
        loads the data from disk"""

        if self.debug:
            print(f"Getting user highlights for user {self.username}")

        # Loading highlights data from the API or from disk
        filename = 'highlights'
        data = self.get_data(filename, update, 'get_user_highlights', self.user_id)
        highlights = [{'title': h['node']['title'], 'id': h['node']['id']} for h in data['data']['user']['edge_highlight_reels']['edges']]

        # Getting stories data for each highlight
        for highlight in highlights:
            filename = f'highlights/{highlight["title"]}'
            data = self.get_data(filename, update, 'get_highlight_stories', highlight['id'])
            highlight['items'] = data['reels'][f'highlight:{highlight["id"]}']['items']
        return highlights

    def download_user_highlights(self, highlights=None, update=False) -> None:
        """
        Download user highlights to disk
        
        Parameters:
        highlights (list): User highlights data. If not provided, gets the data from the API
        update (bool): Whether to update the data if it already exists. If False, 
        loads the data from disk"""

        # Getting user highlights if not provided
        if not highlights:
            highlights = self.get_user_highlights(update=update)

        if self.debug:
            print(f"Downloading user highlights for user {self.username}")

        # Downloading every story in every highlight
        for highlight in highlights:
            self.add_directory(f'highlights/{highlight["title"]}')
            if self.save and not self.data_exists(f'highlights/{highlight["title"]}/data'):
                self.save_json({
                    'title': highlight['title'],
                    'id': highlight['id'],
                    'items': [{
                        'taken_at': item['taken_at'],
                        'id': item['id'],
                        'media_type': 'video' if 'video_versions' in item else 'photo'
                    } for item in highlight['items']]
                }, f'highlights/{highlight["title"]}/data')
            for story in highlight['items']:
                # Skipping if the story was already loaded
                if story['id'] in self.loaded['highlights']:
                    continue

                # Downloading the story
                date = datetime.fromtimestamp(story['taken_at']).strftime('%Y-%m-%d %HH%MM%SS')
                if 'video_versions' in story:
                    self.download_media(story['video_versions'][0]['url'], f'highlights/{highlight["title"]}/story_{date}.mp4')
                else:
                    self.download_media(story['image_versions2']['candidates'][0]['url'], f'highlights/{highlight["title"]}/story_{date}.jpg')

                # Adding the story to the loaded list
                self.loaded['highlights'].append(story['id'])

    def get_user_followers(self, limit=None, update=False) -> dict:
        """
        Get user followers
        
        Parameters:
        update (bool): Whether to update the data if it already exists. If False, 
        loads the data from disk"""

        if self.debug:
            print(f"Getting user followers for user {self.username}")

        if not limit:
            limit = 999_999_999_999

        filename = 'followers/followers_0'
        data = self.get_data(filename, update, 'get_user_followers', self.user_id, 100)

        users = data['users']
        page = 1
        while 'next_max_id' in data and len(users) < limit:
            filename = f'followers/followers_{page}'
            data = self.get_data(filename, update, 'get_user_followers', self.user_id, 100, data['next_max_id'])

            users += data['users']
            page += 1
        return users
    
    def download_user_followers(self, followers=None, limit=None, update=False) -> None:
        """
        Download user followers to disk
        
        Parameters:
        followers (list): User followers data. If not provided, gets the data from the API
        limit (int): Maximum number of followers to download. If not provided, downloads all followers
        update (bool): Whether to update the data if it already exists. If False, 
        loads the data from disk"""

        if not followers:
            followers = self.get_user_followers(limit, update=update)

        if self.debug:
            print(f"Downloading user followers for user {self.username}")

        if self.save and (update or not self.data_exists('followers/followers_full')):
            self.save_json({'users': followers}, 'followers/followers_full')
            self.save_json({'users': [{
                'username': user['username'],
                'id': user['pk']
            } for user in followers]}, 'followers/followers_short')

    def get_user_following(self, limit=None, update=False) -> dict:
        """
        Get user following
        
        Parameters:
        update (bool): Whether to update the data if it already exists. If False, 
        loads the data from disk"""

        if self.debug:
            print(f"Getting user following for user {self.username}")

        if not limit:
            limit = 999_999_999_999

        filename = 'following/following_0'
        data = self.get_data(filename, update, 'get_user_following', self.user_id, 200)

        users = data['users']
        page = 1
        while 'next_max_id' in data and len(users) < limit:
            filename = f'following/following_{page}'
            data = self.get_data(filename, update, 'get_user_following', self.user_id, 200, data['next_max_id'])

            users += data['users']
            page += 1
        return users
    
    def download_user_following(self, following=None, limit=None, update=False) -> None:
        """
        Download user following to disk
        
        Parameters:
        following (list): User following data. If not provided, gets the data from the API
        limit (int): Maximum number of following to download. If not provided, downloads all following
        update (bool): Whether to update the data if it already exists. If False, 
        loads the data from disk"""

        if not following:
            following = self.get_user_following(limit, update=update)

        if self.debug:
            print(f"Downloading user following for user {self.username}")

        if self.save and (update or not self.data_exists('following/following_full')):
            self.save_json({'users': following}, 'following/following_full')
            self.save_json({'users': [{
                'username': user['username'],
                'id': user['pk']
            } for user in following]}, 'following/following_short')

if __name__ == '__main__':
    scraper = UserScraper('starthackclub', True, True)
    scraper.download_user_info()