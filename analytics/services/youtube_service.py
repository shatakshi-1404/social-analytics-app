import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
import random


class YouTubeService:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY

    def search_videos(self, query: str, max_results: int = 20) -> list:
        if not self.api_key:
            return self._mock_youtube_data(query)

        url = f"{self.BASE_URL}/search"
        params = {
            "part": "snippet",
            "q": query,
            "maxResults": min(max_results, 50),
            "type": "video",
            "order": "date",
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            items = response.json().get("items", [])
            video_ids = [item["id"]["videoId"] for item in items if item.get("id", {}).get("videoId")]
            return self._get_video_stats(items, video_ids)
        except requests.RequestException as e:
            print(f"YouTube API error: {e}")
            return self._mock_youtube_data(query)

    def _get_video_stats(self, items: list, video_ids: list) -> list:
        if not video_ids:
            return []
        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": self.api_key,
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception:
            return items

    def _mock_youtube_data(self, query: str) -> list:
        videos = []
        titles = [
            f"Complete Guide to {query} in 2024",
            f"{query} Tutorial for Beginners",
            f"Why {query} is Trending Right Now",
            f"Top 10 Tips for {query}",
            f"{query} Deep Dive - Expert Analysis",
        ]
        for i, title in enumerate(titles):
            videos.append({
                "id": f"mock_yt_{query.replace(' ', '_')}_{i}",
                "snippet": {
                    "title": title,
                    "description": f"An in-depth look at {query} and its impact.",
                    "channelTitle": f"TechChannel{random.randint(1, 99)}",
                    "publishedAt": timezone.now().isoformat(),
                },
                "statistics": {
                    "viewCount": str(random.randint(1000, 1000000)),
                    "likeCount": str(random.randint(100, 50000)),
                    "commentCount": str(random.randint(10, 5000)),
                }
            })
        return videos

    def parse_video(self, raw_video: dict) -> dict:
        snippet = raw_video.get("snippet", {})
        stats = raw_video.get("statistics", {})
        vid_id = raw_video.get("id", "")
        if isinstance(vid_id, dict):
            vid_id = vid_id.get("videoId", "")

        published_str = snippet.get("publishedAt", timezone.now().isoformat())
        try:
            if published_str.endswith('Z'):
                published_str = published_str[:-1] + '+00:00'
            published_at = datetime.fromisoformat(published_str)
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=dt_timezone.utc)
        except Exception:
            published_at = timezone.now()

        return {
            "video_id": vid_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:1000],
            "channel_title": snippet.get("channelTitle", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "published_at": published_at,
        }