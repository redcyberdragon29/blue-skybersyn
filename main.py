import os
import random
import time
from atproto import Client, models
from atproto.exceptions import AtProtocolError
import environs

# Load environment variables
env = environs.Env()
env.read_env()

"""Configuration, put in .env file
example .env file:
DEV_MODE=True
CHECK_INTERVAL=60
BLUESKY_HANDLE=your_handle
BLUESKY_PASSWORD=your_password
"""
DEV_MODE = env.bool("DEV_MODE", default=True)  # Set to True for development mode
CHECK_INTERVAL = env.int("CHECK_INTERVAL", default=60)  # Check every 60 seconds
BLUESKY_HANDLE = env.str("BLUESKY_HANDLE", default="your_handle")
BLUESKY_PASSWORD = env.str("BLUESKY_PASSWORD", default="your_password")


# ReplyManager class to handle replies to posts
class ReplyManager:
    def __init__(self, client):
        self.client = client
        self.my_handle = None

    # get my_handle only once and cache it
    def get_my_handle(self):
        """Get the handle of the bot account"""
        if not self.my_handle:
            profile = self.client.app.bsky.actor.get_profile(
                {"actor": self.client.me.did}
            )
            self.my_handle = profile.handle
        return self.my_handle

    # Check if I've already replied to a post
    def has_replied_to_post(self, post_uri):
        """Check if I've already replied to this post"""
        try:
            # Get my recent posts (including replies)
            my_posts = self.client.app.bsky.feed.get_author_feed(
                {"actor": self.get_my_handle(), "limit": 100}
            )

            # Check if any of my posts are replies to the target post
            for post in my_posts.feed:
                if (
                    hasattr(post, "reply")
                    and post.reply
                    and post.reply.parent.uri == post_uri
                ):
                    return True
            return False
        except Exception as e:
            print(f"Error checking for existing replies: {e}")
            return True  # Default to True to avoid duplicate replies on error


def main():
    client = Client()

    # Login to Bluesky
    try:
        client.login(os.getenv("BLUESKY_HANDLE"), os.getenv("BLUESKY_PASSWORD"))
        print("Logged in successfully!")
    except AtProtocolError as e:
        print(f"Login failed: {e}")
        return

    reply_manager = ReplyManager(client)

    while True:
        try:
            for account in ACCOUNTS_TO_WATCH:
                print(f"Checking posts from {account}...")

                try:
                    posts = client.app.bsky.feed.get_author_feed(
                        {"actor": account, "limit": 5}
                    )
                except Exception as e:
                    print(f"Error getting posts for {account}: {e}")
                    continue

                for post in posts.feed:
                    if not isinstance(post.post.record, models.AppBskyFeedPost.Record):
                        continue

                    post_uri = post.post.uri

                    # Skip if already replied
                    if reply_manager.has_replied_to_post(post_uri):
                        print(f"Already replied to: {post_uri}")
                        continue

                    # Select reply text
                    reply_text = random.choice(REPLIES.get(account, REPLIES["default"]))

                    if DEV_MODE:
                        print(f"[DEV] Would reply to {post_uri}: {reply_text}")
                    else:
                        try:
                            reply_ref = models.AppBskyFeedPost.ReplyRef(
                                root=models.com.atproto.repo.strong_ref.Main(
                                    cid=post.post.cid, uri=post_uri
                                ),
                                parent=models.com.atproto.repo.strong_ref.Main(
                                    cid=post.post.cid, uri=post_uri
                                ),
                            )
                            client.send_post(text=reply_text, reply_to=reply_ref)
                            print(f"Replied to {post_uri}")
                        except Exception as e:
                            print(f"Error sending reply: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")

        print(f"Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)


# Accounts and replies configuration
ACCOUNTS_TO_WATCH = [
    "schumer.senate.gov",
    "slotkin.senate.gov",
    "hakeem-jeffries.bsky.social",
    "fetterman.senate.gov",
    "corybooker.com",
    "kamalaharris.com",
    "governor.ca.gov",
    "gavinnewsom.bsky.social",
]
REPLIES = {
    "default": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
    ],
    "slotkin.senate.gov": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "Your vote for Trump nominees is a betrayal to the people of Michigan, resign.",
        "You care more about posturing against China than serving the people of Michigan, resign.",
        "You lied to the people of Michigan, you are not a progressive, resign.",
    ],
    "schumer.senate.gov": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "Your vote for Trump nominees is a betrayal to the people of New York, resign.",
        "You empowered Trump when you supported the CR, resign!",
        "You have given political cover to a genocide, Israel is starving kids and you support it, resign!",
    ],
    "hakeem-jeffries.bsky.social": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "Primary the spinless democratic leaders like Jeffries!",
        "You complained when your constituants were calling your office? Just wait till the primary!",
        "Wake up, your district is working class, you will get trounced by a progressive in the primary!",
    ],
    "fetterman.senate.gov": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "You have given political cover to a genocide, Israel is starving kids and you support it, resign!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "You betrayed the people of Pensylvania by pretending to be a progressive, resign!",
    ],
    "booker.senate.gov": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "Your fake resistance is a joke, perfect symbolism to do a 24 hour fillibuster to oppose NOTHING!",
        "any more nice wors for Republicans? the Cato Institute can't wait for your next fillibuster!",
        "NJ deserves better than you, resign!",
    ],
    "corybooker.com": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "Your fake resistance is a joke, perfect symbolism to do a 24 hour fillibuster to oppose NOTHING!",
        "NJ deserves better than you, resign!",
    ],
    "kamalaharris.com": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "You lost because you turned your back on economic releif and ending the genocide in Palestine, no one should take you seriously!",
        "Why did you copy Trump's immigration policy? It's so cruel and inhumane!",
        "Why did you refuse to break with Biden on the genocide in  Palestine?",
        "Losers like you should be prevented from running for office in the democratic party! No more Repuiblican-lite!",
        "Who were you trying to appeal to by campaigning with LIZ CHENEY?",
    ],
    "governor.ca.gov": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "You called Abrego Garcia's kidnapping and detention a 'distraction'. Our rights are not a distraction, resign!",
        "You admitted your son likes Charlie Kirk, you're a joke.",
        "Talk to any more fascists on your podcast latley?",
        "You continuoslly stand in the way of progressives in California, you are not the leader we need!",
    ],
    "gavinnewsom.bsky.social": [
        "The people are not falling for your fake progressivism anymore, we see through your lies!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "Democrats need to PRIMARY you out of office, you are not a true representative of the people!",
        "Your actions show you are more interested in serving corporate interests than the people!",
        "You are a sellout to the corporate interests, the people deserve better!",
        "You should just switch parties, people shouldn't mistake you as a supporter of the working class!",
        "People like you are the problem with the democratic party, try standing for the people!",
        "You need to be primaryed out of office, you are not a true representative of the people!",
        "Primary the fake progressives!",
        "You called Abrego Garcia's kidnapping and detention a 'distraction'. Our rights are not a distraction, resign!",
        "You admitted your son likes Charlie Kirk, you're a joke.",
        "Talk to any more fascists on your podcast latley?",
        "You continuoslly stand in the way of progressives in California, you are not the leader we need!",
    ],
}

if __name__ == "__main__":
    main()
