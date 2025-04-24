from mcp.server.fastmcp import FastMCP
import json
from twikit import Client
from typing import List, Dict, Optional
from pathlib import Path
import twikit
import logging
import asyncio
import os


logger = logging.getLogger(__name__)

USERNAME = os.getenv('TWITTER_USERNAME')
EMAIL = os.getenv('TWITTER_EMAIL')
PASSWORD = os.getenv('TWITTER_PASSWORD')
COOKIES_PATH = Path.home() / 'E:\\Agents\\mcp-twitter\\cookies.json'
mcp = FastMCP("twitter-mcp")

async def get_twitter_client() -> twikit.Client:
    """Initialize and return an authenticated Twitter client."""
    client = twikit.Client('en-US')

    if COOKIES_PATH.exists():
        client.load_cookies(COOKIES_PATH)
    else:
        try:
            await client.login(
                auth_info_1=USERNAME,
                auth_info_2=EMAIL,
                password=PASSWORD
            )
        except Exception as e:
            logger.error(f"Failed to login: {e}")
            raise
        COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)
        client.save_cookies(COOKIES_PATH)

    return client

@mcp.tool()
async def get_tweets(query: str, sort_by: str = 'Latest', count: int = 20) -> List[dict]:
    """Search twitter with a query. Sort by 'Top' or 'Latest'"""
    try:
        client = await get_twitter_client()
        tweets = await client.search_tweet(query, sort_by, count=count)

        tweet_data = [get_tweet_data(tweet) for tweet in tweets]
        return tweet_data
    except Exception as e:
        logger.error(f"Error during tweet retrieval: {e}")
        return []

@mcp.tool()
async def get_user_tweets(username: str, tweet_type: str = 'Tweets', count: int = 10) -> str:
    """Get tweets from a specific user's timeline."""
    try:
        client = await get_twitter_client()
        username = username.lstrip('@')
        user = await client.get_user_by_screen_name(username)
        if not user:
            return f"Could not find user {username}"

        tweets = await client.get_user_tweets(
            user_id=user.id,
            tweet_type=tweet_type,
            count=count
        )

        tweet_data = [get_tweet_data(tweet) for tweet in tweets]
        return tweet_data
    except Exception as e:
        logger.error(f"Failed to get user tweets: {e}")
        return f"Failed to get user tweets: {e}"

@mcp.tool()
async def get_replies_for_tweet(tweet_id: str, count: int = 30) -> List[Dict]:
    """
    Get Tweets replies of a specific tweet using tweet_id.
    """

    try:
        # Fetch replies using pagination
        replies = await get_replies(tweet_id, count)

        if replies:
            reply_texts = [reply.text for reply in replies]

            return [get_tweet_data(reply) for reply in replies]
        return []
    except Exception as e:
        logger.error(f"Error fetching replies for tweet {tweet_id}: {e}")
        return []

async def get_replies(tweet_id: str, count: int) -> list:
    """
    Fetch up to `count` replies for a given tweet_id using pagination.
    """
    all_replies = []
    cursor = ""

    try:
        client = await get_twitter_client()

        while len(all_replies) < count:
            try:
                result = await client._get_more_replies(tweet_id, cursor)
                if len(result) == 1:
                    break
            except TooManyRequests as e:
                # rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f"[DEBUG] Rate limit exceeded. Resetting at {datetime.now()}")
                # wait_time = (rate_limit_reset - datetime.now()).total_seconds()
                time.sleep(15)
                continue

            if not hasattr(result, '_Result__results') or not result._Result__results:
                break

            all_replies.extend(result._Result__results)

            if not hasattr(result, 'next_cursor'):
                break

            cursor = result.next_cursor

        return all_replies

    except Exception as e:
        logger.error(f"Error in get_replies: {e}")
        return []

# New write tools
@mcp.tool()
async def post_tweet(
    text: str,
    media_paths: Optional[List[str]] = None,
    reply_to: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """Post a tweet with optional media, reply, and tags."""
    try:

        client = await get_twitter_client()

        # Handle tags by converting to mentions
        if tags:
            mentions = ' '.join(f"@{tag.lstrip('@')}" for tag in tags)
            text = f"""{text}
{mentions}"""

        # Upload media if provided
        media_ids = []
        if media_paths:
            for path in media_paths:
                media_id = await client.upload_media(path, wait_for_completion=True)
                media_ids.append(media_id)

        # Create the tweet
        tweet = await client.create_tweet(
            text=text,
            media_ids=media_ids if media_ids else None,
            reply_to=reply_to
        )
        return f"Successfully posted tweet: {tweet.id}"
    except Exception as e:
        logger.error(f"Failed to post tweet: {e}")
        return f"Failed to post tweet: {e}"

@mcp.tool()
async def delete_tweet(tweet_id: str) -> str:
    """Delete a tweet by its ID."""
    try:
        client = await get_twitter_client()
        await client.delete_tweet(tweet_id)
        return f"Successfully deleted tweet {tweet_id}"
    except Exception as e:
        logger.error(f"Failed to delete tweet: {e}")
        return f"Failed to delete tweet: {e}"


@mcp.tool()
async def get_timeline(count: int = 20) -> str:
    """Get tweets from your home timeline (For You)."""
    try:
        client = await get_twitter_client()
        tweets = await client.get_timeline(count=count)
        return convert_tweets_to_markdown(tweets)
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}")
        return f"Failed to get timeline: {e}"

@mcp.tool()
async def get_latest_timeline(count: int = 20) -> str:
    """Get tweets from your home timeline (Following)."""
    try:
        client = await get_twitter_client()
        tweets = await client.get_latest_timeline(count=count)
        return convert_tweets_to_markdown(tweets)
    except Exception as e:
        logger.error(f"Failed to get latest timeline: {e}")
        return f"Failed to get latest timeline: {e}"

def get_tweet_data(tweet) -> Dict:
    """Enhanced tweet data formatting with additional metrics"""
    try:
        legacy_data = tweet._legacy if hasattr(tweet, '_legacy') else {}
        core_data = tweet._data.get('core', {}) if hasattr(tweet, '_data') else {}
        user_data = core_data.get('user_results', {}).get('result', {}).get('legacy', {})

        text = legacy_data.get('full_text', '')


        return {
            'id': getattr(tweet, 'id', ''),
            'text': text,
            'username': user_data.get('screen_name', 'unknown'),
            'created_at': legacy_data.get('created_at', ''),
            'likes': legacy_data.get('favorite_count', 0),
            'replies': legacy_data.get('reply_count', 0),
            'retweets': legacy_data.get('retweet_count', 0),
            'quote_count': legacy_data.get('quote_count', 0),
        }
    except Exception as e:
        logger.error(f"Error processing tweet data: {e}")
        return {'error': str(e)}



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()