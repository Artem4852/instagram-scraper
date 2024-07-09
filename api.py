import os, dotenv, random, json, requests
from rocketapi import InstagramAPI
from datetime import datetime

dotenv.load_dotenv()

tokens = os.getenv('tokens').split(',')

class UserScraper():
    def __init__(self, user, save=False):
        self.tokens = tokens
        self.apis = [InstagramAPI(token) for token in self.tokens]
        self.save = save
        try: 
            self.user_id = int(user)
            self.username = self.get_username(self.user_id)
        except: 
            self.username = user
            self.user_id = self.get_user_id(self.username)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

    def random_api(self):
        return random.choice(self.apis)
    
    def save_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f)

    def get_user_id(self, username):
        data = self.random_api().get_user_info(username)
        if self.save: self.save_json(data, 'user_info.json')
        return int(data['data']['user']['id'])

    def get_username(self, user_id):
        data = self.random_api().get_user_info_by_id(user_id)
        if self.save: self.save_json(data, 'user_info.json')
        return data['user']['username']
    
    def get_user_info(self, user_id):
        data = self.random_api().get_user_info_by_id(user_id)
        if self.save: self.save_json(data, 'user_info.json')
        return data['user']
    
    def download_user_info(self, user_info=None):
        if not user_info: user_info = self.get_user_info(self.user_id)
        os.makedirs(f'{self.username}', exist_ok=True)
        if self.save_json: self.save_json(user_info, f'{self.username}/user_info.json')
        with open(f'{self.username}/user_info.txt', "w") as f:
            f.write(f"Username: {user_info['username']}\n")
            f.write(f"User ID: {user_info['pk']}\n")
            f.write(f"Full Name: {user_info['full_name']}\n")
            f.write(f"Biography: {user_info['biography']}\n")
            f.write(f"Followers: {user_info['follower_count']}\n")
            f.write(f"Following: {user_info['following_count']}\n")
            f.write(f"Posts: {user_info['media_count']}\n")
        r = requests.get(user_info['hd_profile_pic_url_info']['url'], headers=self.headers)
        with open(f'{self.username}/propic.jpg', 'wb') as f:
            f.write(r.content)
    
    def get_user_posts(self, limit=None):
        if not limit: limit = 999999
        data = self.random_api().get_user_media(self.user_id, 50)
        if self.save: self.save_json(data, 'user_posts_0.json')
        posts = data['items']
        page = 1
        while data['more_available'] and len(posts) < limit:
            data = self.random_api().get_user_media(self.user_id, 50, data['next_max_id'])
            if self.save: self.save_json(data, f'user_posts_{page}.json')
            posts += data['items']
            page += 1
        return posts
    
    def download_user_posts(self, posts=None, limit=None):
        if not posts: posts = self.get_user_posts(limit)
        os.makedirs(f'{self.username}/posts', exist_ok=True)
        if self.save_json: self.save_json(posts, f'{self.username}/posts.json')
        for post in posts:
            date = datetime.fromtimestamp(post['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
            os.makedirs(f'{self.username}/posts/post_{date}', exist_ok=True)
            with open(f'{self.username}/posts/post_{date}/caption.txt', 'w') as f:
                f.write(post['caption']['text'])
            images = [im['image_versions2']['candidates'][0]['url'] for im in post['carousel_media']]
            for i, image in enumerate(images):
                r = requests.get(image, headers=self.headers)
                with open(f'{self.username}/posts/post_{date}/{i}.jpg', 'wb') as f:
                    f.write(r.content)

    def get_user_stories(self):
        data = self.random_api().get_user_stories(self.user_id)
        if self.save: self.save_json(data, 'user_stories.json')
        return data['reels'][str(self.user_id)]['items']
    
    def download_user_stories(self, stories=None):
        if not stories: stories = self.get_user_stories()
        os.makedirs(f'{self.username}/stories', exist_ok=True)
        if self.save_json: self.save_json(stories, f'{self.username}/stories.json')
        for story in stories:
            date = datetime.fromtimestamp(story['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
            r = requests.get(story['image_versions2']['candidates'][0]['url'], headers=self.headers)
            with open(f'{self.username}/stories/story_{date}.jpg', 'wb') as f:
                f.write(r.content)

    def get_user_highlights(self):
        data = self.random_api().get_user_highlights(self.user_id)
        if self.save: self.save_json(data, 'user_highlights.json')
        highlights = [{'title': h['node']['title'], 'id': h['node']['id']} for h in data['data']['user']['edge_highlight_reels']['edges']]
        for highlight in highlights:
            data = self.random_api().get_highlight_stories(highlight['id'])
            if self.save: self.save_json(data, f'{highlight["title"]}.json')
            highlight['items'] = data['reels'][f'highlight:{highlight["id"]}']['items']
        return highlights

if __name__ == '__main__':
    scraper = UserScraper('starthackclub', True)
    scraper.download_user_info()
    # scraper.download_user_posts(limit=50)
    scraper.download_user_stories()