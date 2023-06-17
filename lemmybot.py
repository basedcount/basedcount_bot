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
community_id = '!pcm'  # Replace with the desired community ID
comments = post.list(community_id=community_id, type_=ListingType.COMMENTS, sort=SortType.ACTIVITY)
'''
# Iterate through the comments
for comment in comments:
    if comment["body"].startswith("Based"):
        # Reply to the comment
        post.create(community_id, "Your reply message", comment_id=comment["id"])'''