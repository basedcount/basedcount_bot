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


comments = lemmy.post.get_latest_comments(2, 1)

size = len(comments["comments"])
print("Size of comments_data:", size)

if "comments" in comments:
    comments = comments["comments"]

    for comment in comments:

        user = comment["creator"]["name"]
        body = comment["comment"]["content"]
        published = comment["comment"]["published"]
        post_id = comment["comment"]["post_id"]

        commentid = comment["comment"]["id"]
        path = comment["comment"]["path"]
        path_elements = path.split(".")
        parent_comment_id = int(path_elements[-2])

        parent_comment = lemmy.post.get(post_id, comment_id=parent_comment_id)
        parent = parent_comment['post_view']['creator']['name']

        print("User:", user)
        print("Body:", body)
        print("Published:", published)
        print("Comment ID:", commentid)
        print("Parent Comment ID:", parent_comment_id)
        print("Parent:", parent)

else:
    print("No comments found.")
