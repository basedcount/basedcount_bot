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
community_id = 2 # PCM

post = Post()

counted_comments = []

while True:
    try:
        print('Searching...')
        
        comments = lemmy.post.get_latest_comments(community_id=2, max_depth=10)

        # Weird check to see if Lemmy actually sent a comments list
        if "comments" in comments:
            comments = comments["comments"]

            # Get initial data to see if action is necessary
            for comment in comments:
                body = comment["comment"]["content"]
                commentid = comment["comment"]["id"]
                
                # Check if based comment, also check if already counted
                if body.startswith(('Based', 'based')) and not body.startswith('basedcount'):
                    newComment = True
                    for idnum in counted_comments:
                        if commentid == idnum:
                            newComment = False
                            break

                    # Parse comment data and prepare for parent search
                    if newComment:
                        counted_comments.append(commentid)
                        user = comment["creator"]["name"]
                        published = comment["comment"]["published"]
                        post_id = comment["comment"]["post_id"]
                        path = comment["comment"]["path"]
                        path_elements = path.split(".")
                        parent_comment_id = int(path_elements[-2])
                        
                        # Parent is a comment
                        try:
                            parent_comment = lemmy.post.get_comment(post_id=parent_comment_id)
                            parent = parent_comment['comment_view']['creator']['name']
                        
                        # Parent is a post, still throws error
                        except:
                            parent_comment = lemmy.post.get(post_id=post_id)
                            parent = parent_comment['post_view']['creator']['name']
                        
                        # Make sure parent isn't self
                        if parent != 'basedcount_bot':
                            #lemmy.post.write_comment(post_id, commentid, f"{parent}'s Based Count has increased by 1.")
                            print(f"{parent}'s Based Count has increased by 1.")
               
        else:
            print("No comments found.")

    except:
        print('Oopsie poopsie!')
    
    time.sleep(10)
