import praw
import pygame
from dotenv import load_dotenv
import logging
import os
import re

load_dotenv()

# Set up logger
def set_logger(log_file = 'app.log'):
    logger = logging.getLogger('simple_logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

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

if __name__ == '__main__':
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
        if user_input == 'q':
            break

# Dict for flags depending on sentiment analysis
flag_dict = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "⚪", "Strong Bullish": "🟢🟢", "Trade Halt Scare": "🛑", "Market Crash": "🔻", "CRITICAL ALERT": "🚨🚨🚨"}

# Temp test values
summary = "test2"
action = "test3"
flag = "test1"

# Test REGEX
crypto_regex = re.compile(r"\b(btc|bitcoin|eth|ethereum|sol|solana|\$[a-z]{2,5})\b", re.IGNORECASE)



# Reddit app credentials
reddit = praw.Reddit(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        user_agent = os.getenv("USER_AGENT")

)

# Selected Crypto subreddits TODO: Give user option to add different reddits based on preference
subreddit = reddit.subreddit('CryptoCurrency+ethfinance+Bitcoin+ethstaker+cryptomarkets+altcoin+defi+solana')

# Fetch recent posts
for post in subreddit.hot(limit=50):
    print(f"Title: {post.title}")
    print(f"Subreddit: {post.subreddit}")
    print(f"Upvotes: {post.score}")
    print(f"Story: {post.selftext}")
    print(f"Posted by: u/{post.author}")
    print(f"Link: https://reddit.com{post.permalink}")
    print("-" * 60)
    print(f"LLM Summarized: {summary}")
    print(f"Sentiment Flag: {flag}")
    print(f"Suggested Action: {action}")
    # TEST FOR WARNING SOUND NOT PRODUCTION!!
    if post.score <= 78:
        play_warning()
