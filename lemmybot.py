from pythorhead import Lemmy
from pythorhead.types import ListingType, SortType
from pythorhead.post import Post
import os
from dotenv import load_dotenv
import time

load_dotenv()
username = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')
lemmy = Lemmy("https://forum.basedcount.com")
lemmy.log_in(username, password)
community_id = 2  # Replace with the desired community ID

post = Post()

counted_comments = []

while True:
    try:
        print('starting')
        
        comments = lemmy.post.get_latest_comments(community_id=2, max_depth=10)

        if "comments" in comments:
            comments = comments["comments"]

            for comment in comments:

                counted_and_replied = False
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
                
                if parent != 'basedcount_bot':
                    if body.startswith(('Based', 'based')):
                        for idnum in counted_comments:
                            if commentid == idnum:
                                counted_and_replied = True
                        if counted_and_replied == False:
                            #lemmy.post.write_comment(post_id, commentid, f"{parent}'s Based Count has increased by 1.")
                            print(f"{parent}'s Based Count has increased by 1.")
                            counted_comments.append(commentid)

        else:
            print("No comments found.")
        time.sleep(10)
    except:
        print('Oopsie poopsie!')
