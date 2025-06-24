import logging
import os
import re
import math
from datetime import datetime
import praw
import pygame
import colorama
from uuid import uuid4
from dotenv import load_dotenv
from cassandra.cluster import Cluster

load_dotenv()


# Reddit Env Variables
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT"),
)


# Cassandra Env Variables
clust = os.getenv("CLUSTER")
cluster = Cluster([clust])
csession = os.getenv("SESSION")
session = cluster.connect(csession)

# Cassandra Table Function
def insert_cassandra(title, subreddit, score, story, user):
    session.execute(
        """
        INSERT INTO signals (id, timestamp, subreddit, title, score, story, user)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (uuid4(), datetime.now(), subreddit, title, score, story, user),
    )

# Set up logger
def set_logger(log_file="app.log"):
    logger = logging.getLogger("simple_logger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    logger = set_logger()

# Warning Noise
def play_warning():
    while True:
        pygame.mixer.init()
        pygame.mixer.music.load("alarm-301729.mp3")
        pygame.mixer.music.play()
        user_input = input("Press 'q' to quit: ")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        if user_input == "q":
            break


# Dict for flags depending on sentiment analysis
flag_dict = {
    "Bullish": "🟢",
    "Bearish": "🔴",
    "Neutral": "⚪",
    "Strong Bullish": "🟢🟢",
    "Trade Halt Scare": "🛑",
    "Market Crash": "🔻",
    "CRITICAL ALERT": "🚨🚨🚨",
}

# Temp test values
summary = "test2"
action = "test3"
flag = "test1"

# IGNORE CRYPTO REGEX UNTIL SELECTIONAL FILTERING
# crypto_regex = re.compile(r"\b(btc|bitcoin|eth|ethereum|sol|solana|\$[a-z]{2,5})\b", re.IGNORECASE)

# Selected Crypto subreddits TODO: Give user option to add different reddits based on preference
subreddit_list = ["CryptoCurrency", "Bitcoin", "ethereum", "ethtrader"]

for name in subreddit_list:
    print(f"\nPulling From r/{name}")
    subreddit = reddit.subreddit(name)

    # dummy variables
    summary = "test2"
    action = "test3"
    flag = "test1"
    dummy_score = 0.5
    dummy_decision = "HOLD"

    # Fetch recent posts
    for post in subreddit.hot(limit=50):
        if (
            # post.score <= 10 or
            # post.num_comments < 3 or
            post.author is None
            or (post.author.comment_karma < 100 and post.author.link_karma < 50)
            or
            # len(post.title) < 10 or
            any(
                prohib_word in post.title.lower()
                for prohib_word in ["airdrop", "giveaway", "nft", "win", "dm me"]
            )
        ):
            continue
        print("-" * 60)
        print(f"Title: {post.title}")
        print(f"Subreddit: {post.subreddit}")
        print(f"Upvotes: {post.score}")
        print("Story", repr(post.selftext))
        print(f"Posted by: u/{post.author}")
        print(f"Link: https://reddit.com{post.permalink}")
        print("-" * 60)
        print(f"LLM Summarized: {summary}")
        print(f"Sentiment Flag: {flag}")
        print(f"Suggested Action: {action}")

        insert_cassandra(
            post.title,
            str(post.subreddit),
            float(post.score),
            str(post.selftext),
            str(post.author.name) if post.author else "unknown",
        )
        # TEST FOR WARNING SOUND NOT PRODUCTION!!
    # if post.score >= 10:
    #    play_warning()

