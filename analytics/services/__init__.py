# analytics/services/twitter_service.py
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone


class TwitterService:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json",
        }

    def search_recent_tweets(self, query: str, max_results: int = 50) -> list:
        """Search recent tweets for a query/keyword."""
        if not settings.TWITTER_BEARER_TOKEN:
            return self._mock_twitter_data(query)

        url = f"{self.BASE_URL}/tweets/search/recent"
        params = {
            "query": f"{query} -is:retweet lang:en",
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,author_id,text",
            "expansions": "author_id",
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            print(f"Twitter API error: {e}")
            return self._mock_twitter_data(query)

    def _mock_twitter_data(self, query: str) -> list:
        """Return mock data when API key is not available."""
        import random
        tweets = []
        sample_texts = [
            f"Really excited about {query}! The community is growing fast. #trending",
            f"Just discovered {query} and I'm blown away by the possibilities",
            f"{query} is changing the game for content creators everywhere",
            f"Had a great experience with {query} today. Highly recommend checking it out!",
            f"The latest updates to {query} are incredible. This is the future.",
            f"Not sure about {query} yet. Need more time to evaluate the pros and cons.",
            f"Warning: {query} has some serious issues that need to be addressed ASAP",
            f"{query} community meetup was amazing! So many brilliant minds in one place",
        ]
        for i, text in enumerate(sample_texts):
            tweets.append({
                "id": f"mock_{query.replace(' ', '_')}_{i}",
                "text": text,
                "author_id": f"user_{random.randint(1000, 9999)}",
                "created_at": timezone.now().isoformat(),
                "public_metrics": {
                    "retweet_count": random.randint(0, 500),
                    "like_count": random.randint(10, 5000),
                    "reply_count": random.randint(0, 200),
                }
            })
        return tweets

    def parse_tweet(self, raw_tweet: dict) -> dict:
        metrics = raw_tweet.get("public_metrics", {})
        created_str = raw_tweet.get("created_at", timezone.now().isoformat())
        try:
            if created_str.endswith('Z'):
                created_str = created_str[:-1] + '+00:00'
            created_at = datetime.fromisoformat(created_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=dt_timezone.utc)
        except Exception:
            created_at = timezone.now()

        return {
            "tweet_id": raw_tweet.get("id", ""),
            "text": raw_tweet.get("text", ""),
            "author_id": raw_tweet.get("author_id", ""),
            "retweet_count": metrics.get("retweet_count", 0),
            "like_count": metrics.get("like_count", 0),
            "reply_count": metrics.get("reply_count", 0),
            "created_at": created_at,
        }