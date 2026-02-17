import os
import random
import time
from atproto import Client, models
from atproto.exceptions import AtProtocolError
import environs
import datetime

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

class ReplyManager:
    def __init__(self, client):
        self.client = client
        self.my_handle = None

    def get_my_handle(self):
        """Get the handle of the bot account"""
        if not self.my_handle:
            profile = self.client.app.bsky.actor.get_profile(
                {"actor": self.client.me.did}
            )
            self.my_handle = profile.handle
        return self.my_handle

    def has_replied_to_post(self, post_uri):
        """Check if I've already replied to this post"""
        try:
            my_posts = self.client.app.bsky.feed.get_author_feed(
                {"actor": self.get_my_handle(), "limit": 100}
            )

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
            return True

    def send_reply_with_link_preview(self, post_uri, post_cid, reply_text, url=None):
        """Send reply with guaranteed link preview"""
        try:
            # Create the reply reference
            reply_ref = models.AppBskyFeedPost.ReplyRef(
                root=models.com.atproto.repo.strong_ref.Main(
                    cid=post_cid, uri=post_uri
                ),
                parent=models.com.atproto.repo.strong_ref.Main(
                    cid=post_cid, uri=post_uri
                ),
            )

            # If URL exists in reply text, create an embed
            embed = None
            if url:
                # Create external embed for link preview
                embed = models.AppBskyEmbedExternal.Main(
                    external=models.AppBskyEmbedExternal.External(
                        uri=url,
                        title="",  # Auto-generated from page
                        description=""  # Auto-generated from page
                    )
                )
                # Ensure URL appears in text
                if url not in reply_text:
                    reply_text = f"{url}\n\n{reply_text}"

            # Send the post
            self.client.send_post(
                text=reply_text,
                reply_to=reply_ref,
                embed=embed
            )
            return True
        except Exception as e:
            print(f"Error sending reply with preview: {e}")
            return False

def extract_url_from_text(text):
    """Extract first URL from text if present"""
    import re
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls[0] if urls else None

def main():
    client = Client()

    try:
        client.login(os.getenv("BLUESKY_HANDLE"), os.getenv("BLUESKY_PASSWORD"))
        print("Logged in successfully!")
    except AtProtocolError as e:
        print(f"Login failed: {e}")
        return

    reply_manager = ReplyManager(client)
    # Convert to set for faster lookups
    watched_accounts = set(ACCOUNTS_TO_WATCH)

    while True:
        try:
            for account in ACCOUNTS_TO_WATCH:
                print(f"Checking posts from {account}...")

                try:
                    posts = client.app.bsky.feed.get_author_feed(
                        {"actor": account, "limit": 1}
                    )
                except Exception as e:
                    print(f"Error getting posts for {account}: {e}")
                    continue

                for post in posts.feed:
                    if not isinstance(post.post.record, models.AppBskyFeedPost.Record):
                        continue

                    # Verify post author is in our watch list
                    post_author = post.post.author.handle
                    if post_author not in watched_accounts:
                        print(f"Skipping reply to {post_author} (not in watch list)")
                        continue

                    post_uri = post.post.uri
                    post_cid = post.post.cid

                    if reply_manager.has_replied_to_post(post_uri):
                        print(f"Already replied to: {post_uri}")
                        continue

                    reply_text = random.choice(REPLIES.get(post_author, REPLIES["default"]))
                    url = extract_url_from_text(reply_text)

                    if DEV_MODE:
                        print(f"[DEV] Would reply to {post_uri}: {reply_text}")
                        if url:
                            print(f"[DEV] Would include link preview for: {url}")
                    else:
                        try:
                            if url:
                                success = reply_manager.send_reply_with_link_preview(
                                    post_uri,
                                    post_cid,
                                    reply_text,
                                    url
                                )
                            else:
                                reply_ref = models.AppBskyFeedPost.ReplyRef(
                                    root=models.com.atproto.repo.strong_ref.Main(
                                        cid=post_cid, uri=post_uri
                                    ),
                                    parent=models.com.atproto.repo.strong_ref.Main(
                                        cid=post_cid, uri=post_uri
                                    ),
                                )
                                client.send_post(text=reply_text, reply_to=reply_ref)
                                success = True
                            
                            if success:
                                print(f"Replied to {post_uri}")
                        except Exception as e:
                            print(f"Error sending reply: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")

        print(f"Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)

# Accounts and replies configuration
ACCOUNTS_TO_WATCH = [
    "vanhollen.senate.gov",
    "raskin.house.gov",
    "alsobrooks.senate.gov",
    "schumer.senate.gov",
    "slotkin.senate.gov",
    "hakeem-jeffries.bsky.social",
    "fetterman.senate.gov",
    "corybooker.com",
    "kamalaharris.com",
    "governor.ca.gov",
    "washingtonpost.com"
]

# replies dictionary 
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
    "vanhollen.senate.gov": [
        "Another one of your constituents, with an open asylum case, got abducted by ICE. WE DEMAND ACTION! https://gofund.me/bb59d045"
        ],
    "raskin.house.gov": [
        "One of your constituents, with an open asylum case, got abducted by ICE. WE DEMAND ACTION! https://gofund.me/bb59d045"
        ],
    "alsobrooks.senate.gov": [
        "Another one of your constituents, with an open asylum case, got abducted by ICE. WE DEMAND ACTION! https://gofund.me/bb59d045"
        ],
    "slotkin.senate.gov": [
        "Your vote for Trump nominees is a betrayal to the people of Michigan, resign.",
        "You care more about posturing against China than serving the people of Michigan, resign.",
        "AIPAC puppet, resign!",
        "Ex-CIA, pro-war piece of shit!",
        "Sinophobic, rascist loser. Trying to ban Chinese cars while Trump ruins the economy with tarriffs!",
        "Crypto Shill!",
        "You're a CIA asshole. Your mod squad is a joke. Move over for the progressives, you're done." 
    ],
    "schumer.senate.gov": [
        "Your vote for Trump nominees is a betrayal to the people of New York, resign.",
        "You empowered Trump when you supported the CR, resign!",
        "You have given political cover to a genocide, Israel is starving kids and you support it, resign!",
        "What are your marching orders from Goldman-Sachs, you corrupt loser?",
        "You enable genocide in Gaza while NYers demand divestment. History will remember your complicity.",
        "Start looking for a retirement home."
    ],
    "hakeem-jeffries.bsky.social": [
        "You complained when your constituants were calling your office? Just wait till the primary!",
        "Median household income of $65000/year in your district and you sell out to wall street EVERY TIME. A mild primary challenge will end you."
        "Wake up, your district is working class, you will get trounced by a progressive in the primary!",
        "There are alot of Mamdani voters in your district. You will not survive a primary, enjoy your remaining time in office!",
        "The Mamdani wave is coming for you.....",
        "Despite representing Brooklyn, you seem to care way more about wallstreet. Why did you let Citi bank write banking regulations?",
        "Start looking for a retirement home."
    ],
    "fetterman.senate.gov": [
        "You have given political cover to a genocide, Israel is starving kids and you support it, resign!",
        "You are a disgrace to the democratic party, your actions show you don't care about the people!",
        "You betrayed the people of Pensylvania by pretending to be a progressive, resign!",
        "Traitor PoS.",
        "Lazy, dumb, fake asshole.",
        "get fucked you genocider asshole."
    ],
    "booker.senate.gov": [
        "Your fake resistance is a joke, perfect symbolism to do a 24 hour fillibuster to oppose NOTHING!",
        "any more nice words for Republicans? The Cato Institute can't wait for your next fillibuster!",
        "NJ deserves better than you, resign!",
        "You are so fake. A progressive will destroy you in the primary. Ask Cuomo",
        "The Mamdani wave is coming for you.....",
        "Baby killer! The people of Gaza are starving and you support it!",
    ],
    "corybooker.com": [
        "Your fake resistance is a joke, perfect symbolism to do a 24 hour fillibuster to oppose NOTHING!",
        "any more nice words for Republicans? The Cato Institute can't wait for your next fillibuster!",
        "NJ deserves better than you, resign!",
        "Democrats' opposition is a joke, time to primary every one of you mother fuckers!",
        "Baby killer! The people of Gaza are starving and you support it!",
        "The Mamdani wave is coming for you.....",
    ],
    "kamalaharris.com": [
        "You lost because you turned your back on economic releif and ending the genocide in Palestine, no one should take you seriously!",
        "Why did you copy Trump's immigration policy? It's so cruel and inhumane!",
        "Why did you refuse to break with Biden on the genocide in  Palestine?",
        "Losers like you should be prevented from running for office in the democratic party! No more Repuiblican-lite!",
        "Who were you trying to appeal to by campaigning with LIZ CHENEY?",
    ],
    "governor.ca.gov": [
        "Will you commit to defying the supreme court if they rule against your congressional map?",
        "Commit to defying the supreme court if they rule against your congressional map!",
        "Will you bend to the corrupt supreme court and allow them to strike down your congressional map?",
        "You have done nothing to protect migrants and CALIFORNIA COPS are beating protestors",
        "You have done nothing to protect migrants and CALIFORNIA COPS are complicit in the abduction of migrants!",
        "WHERE ARE THE STATE RESOURCES TO PROTECT MIGRANTS GOVERNOR?",
        "A worker died hiding from ICE in your state and you arent protecting anyone!",
    ],
    "washingtonpost.com": [
        "This paper is manufacturing consent for the OCCUPATION OF DC!",
        "Why are you legitimizing Trumps' narrative of crime in DC?",
        "You are complicit in the OCCUPATION OF DC!",
    ]

}

if __name__ == "__main__":
    main()
