import pythorhead

from pythorhead.pythorhead import Lemmy
from pythorhead.pythorhead.types import ListingType, SortType

lemmy = Lemmy("https://lemmy.dbzer0.com")
lemmy.log_in("username", "password")

post = pythorhead.Post()

# Retrieve comments from a specific community or post
community_id = 123  # Replace with the desired community ID
comments = post.list(community_id=community_id, type_=ListingType.COMMENTS, sort=SortType.ACTIVITY)

# Iterate through the comments
for comment in comments:
    if comment["body"].startswith("Based"):
        # Reply to the comment
        post.create(community_id, "Your reply message", comment_id=comment["id"])