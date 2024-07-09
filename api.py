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
            self.username = None
            self.username = self.get_username(self.user_id)
        except: 
            self.username = user
            self.user_id = self.get_user_id(self.username)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        self.loaded = self.load_loaded()
        os.makedirs(f'{self.username}', exist_ok=True)

    def random_api(self):
        return random.choice(self.apis)
    
    def load_loaded(self):
        if not os.path.exists(f'{self.username}/loaded.json'): return {'posts': [], 'stories': [], 'highlights': []}
        with open(f'{self.username}/loaded.json', 'r') as f: return json.load(f)

    def save_loaded(self):
        with open(f'{self.username}/loaded.json', 'w') as f: json.dump(self.loaded, f)

    def save_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f)

    def get_user_id(self, username, update=False):
        filename = f'{username}/user_info_basic.json'
        if update or not os.path.exists(filename):
            data = self.random_api().get_user_info(username)
            if self.save: self.save_json(data, filename)
        else:
            with open(filename, 'r') as f: data = json.load(f)
        return int(data['data']['user']['id'])

    def get_username(self, user_id):
        data = self.random_api().get_user_info_by_id(user_id)
        filename = f"{data['user']['username']}/user_info.json"
        if self.save: self.save_json(data, filename)
        return data['user']['username']
    
    def get_user_info(self, user_id, update=False):
        filename = f'{self.username}/user_info.json'
        if update or not os.path.exists(filename):
            data = self.random_api().get_user_info_by_id(user_id)
            if self.save: self.save_json(data, filename)
        else:
            with open(filename, 'r') as f: data = json.load(f)
        return data
    
    def download_user_info(self, user_info=None, update=False):
        if not user_info: user_info = self.get_user_info(self.user_id, update=update)
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
    
    def get_user_posts(self, limit=None, update=False):
        if not limit: limit = 999999
        os.makedirs(f'{self.username}/posts', exist_ok=True)
        filename = f'{self.username}/posts/posts_0.json'
        if update or not os.path.exists(filename):
            data = self.random_api().get_user_media(self.user_id, 50)
            if self.save: self.save_json(data, filename)
        else:
            with open(filename, 'r') as f: data = json.load(f)
        posts = data['items']
        page = 1
        while data['more_available'] and len(posts) < limit:
            filename = f'{self.username}/posts/posts_{page}.json'
            if update or not os.path.exists(filename):
                data = self.random_api().get_user_media(self.user_id, 50, data['next_max_id'])
                if self.save: self.save_json(data, filename)
            else:
                with open(filename, 'r') as f: data = json.load(f)
            posts += data['items']
            page += 1
        return posts
    
    def download_user_posts(self, posts=None, limit=None, update=False):
        if not posts: posts = self.get_user_posts(limit, update=update)
        os.makedirs(f'{self.username}/posts', exist_ok=True)
        if self.save_json: self.save_json(posts, f'{self.username}/posts.json')
        for n, post in enumerate(posts):
            if n >= limit: break
            date = datetime.fromtimestamp(post['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
            os.makedirs(f'{self.username}/posts/post_{date}', exist_ok=True)
            self.save_json({'data': post}, f'{self.username}/posts/post_{date}/data.json')

            if 'carousel_media' in post: images = [im for im in post['carousel_media']]
            else: images = [post]
            for i, image in enumerate(images):
                if image['id'] in self.loaded['posts']: continue
                if 'video_versions' in image:
                    r = requests.get(image['video_versions'][0]['url'], headers=self.headers)
                    with open(f'{self.username}/posts/post_{date}/{i}.mp4', 'wb') as f:
                        f.write(r.content)
                else:
                    r = requests.get(image['image_versions2']['candidates'][0]['url'], headers=self.headers)
                    with open(f'{self.username}/posts/post_{date}/{i}.jpg', 'wb') as f:
                        f.write(r.content)
                self.loaded['posts'].append(image['id'])
                self.save_loaded()
            if not 'caption' in post: continue
            if not post['caption']: continue
            if not 'text' in post['caption']: continue
            with open(f'{self.username}/posts/post_{date}/caption.txt', 'w') as f:
                f.write(post['caption']['text'])

    def get_user_stories(self):
        data = self.random_api().get_user_stories(self.user_id)
        if self.save: self.save_json(data, 'user_stories.json')
        return data['reels'][str(self.user_id)]['items']
    
    def download_user_stories(self, stories=None):
        if not stories: stories = self.get_user_stories()
        os.makedirs(f'{self.username}/stories', exist_ok=True)
        if self.save_json: self.save_json(stories, f'{self.username}/stories.json')
        for story in stories:
            if story['id'] in self.loaded['stories']: continue
            date = datetime.fromtimestamp(story['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
            if 'video_versions' in story:
                r = requests.get(story['video_versions'][0]['url'], headers=self.headers)
                with open(f'{self.username}/stories/story_{date}.mp4', 'wb') as f:
                    f.write(r.content)
            else:
                r = requests.get(story['image_versions2']['candidates'][0]['url'], headers=self.headers)
                with open(f'{self.username}/stories/story_{date}.jpg', 'wb') as f:
                    f.write(r.content)
            self.loaded['stories'].append(story['id'])
            self.save_loaded()

    def get_user_highlights(self, update=False):
        filename = f'{self.username}/highlights.json'
        if update or not os.path.exists(filename):
            data = self.random_api().get_user_highlights(self.user_id)
            if self.save: self.save_json(data, filename)
        else:
            with open(filename, 'r') as f: data = json.load(f)
        highlights = [{'title': h['node']['title'], 'id': h['node']['id']} for h in data['data']['user']['edge_highlight_reels']['edges']]
        for highlight in highlights:
            filename = f'{self.username}/highlights/{highlight["title"]}.json'
            if update or not os.path.exists(filename):
                data = self.random_api().get_highlight_stories(highlight['id'])
                if self.save: self.save_json(data, filename)
            else:
                with open(filename, 'r') as f: data = json.load(f)
            highlight['items'] = data['reels'][f'highlight:{highlight["id"]}']['items']
        return highlights
    
    def download_user_highlights(self, highlights=None, update=False):
        if not highlights: highlights = self.get_user_highlights(update=update)
        os.makedirs(f'{self.username}/highlights', exist_ok=True)
        if self.save_json: self.save_json(highlights, f'{self.username}/highlights.json')
        for highlight in highlights:
            os.makedirs(f'{self.username}/highlights/{highlight["title"]}', exist_ok=True)
            self.save_json({'data': highlight}, f'{self.username}/highlights/{highlight["title"]}/data.json')
            for story in highlight['items']:
                if story['id'] in self.loaded['highlights']: continue
                date = datetime.fromtimestamp(story['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
                if 'video_versions' in story:
                    r = requests.get(story['video_versions'][0]['url'], headers=self.headers)
                    with open(f'{self.username}/highlights/{highlight["title"]}/story_{date}.mp4', 'wb') as f:
                        f.write(r.content)
                else:
                    r = requests.get(story['image_versions2']['candidates'][0]['url'], headers=self.headers)
                    with open(f'{self.username}/highlights/{highlight["title"]}/story_{date}.jpg', 'wb') as f:
                        f.write(r.content)
                self.loaded['highlights'].append(story['id'])

if __name__ == '__main__':
    scraper = UserScraper('starthackclub', True)
    scraper.download_user_info()
    scraper.download_user_posts(limit=10)
    scraper.download_user_stories()
    print(2)
    scraper.download_user_highlights()