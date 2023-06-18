from pythorhead import Lemmy
from pythorhead.types import ListingType, SortType
from pythorhead.post import Post
import os
from dotenv import load_dotenv

load_dotenv()
username = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')
lemmy = Lemmy("https://forum.basedcount.com")
lemmy.log_in(username, password)

post = Post()

# Retrieve comments from a specific community or post
community_id = 2  # Replace with the desired community ID


post = lemmy.post.get(post_id=145)

# Access post information
print(f"Post ID: {post['post_view']['post']['id']}")
print(f"Post Title: {post['post_view']['post']['name']}")
# ...

