import anthropic
from django.conf import settings
import json
import re


class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None

    def analyze_trends(self, topic_name: str, platform: str, content_list: list) -> dict:
        """Use Claude to analyze content and generate trend summary."""
        if not self.client or not content_list:
            return self._mock_analysis(topic_name, platform, content_list)

        content_text = "\n".join([f"- {c}" for c in content_list[:30]])
        prompt = f"""You are a social media analytics expert. Analyze the following {platform} content about "{topic_name}".

Content samples:
{content_text}

Provide a JSON response with exactly these fields:
{{
  "summary": "2-3 sentence summary of the overall trend",
  "sentiment": "positive|negative|neutral|mixed",
  "sentiment_score": float between -1.0 and 1.0,
  "key_themes": ["theme1", "theme2", "theme3"],
  "trending_keywords": ["word1", "word2", "word3", "word4", "word5"],
  "engagement_score": float between 0 and 100,
  "insights": "one actionable insight for content creators"
}}

Return ONLY valid JSON, no markdown or extra text."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            text = message.content[0].text.strip()
            # Strip markdown code fences if present
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._mock_analysis(topic_name, platform, content_list)

    def _mock_analysis(self, topic_name: str, platform: str, content_list: list) -> dict:
        import random
        sentiments = ['positive', 'negative', 'neutral', 'mixed']
        sentiment = random.choice(sentiments)
        score_map = {'positive': 0.7, 'negative': -0.6, 'neutral': 0.0, 'mixed': 0.1}
        return {
            "summary": f"Analysis of {len(content_list)} {platform} posts about {topic_name} shows strong community engagement with diverse perspectives emerging across the platform.",
            "sentiment": sentiment,
            "sentiment_score": score_map[sentiment] + random.uniform(-0.2, 0.2),
            "key_themes": [f"{topic_name} growth", "community discussion", "expert opinions", "tutorials"],
            "trending_keywords": [topic_name, "trending", "viral", "community", "2024"],
            "engagement_score": random.uniform(40, 90),
            "insights": f"Content about {topic_name} is performing well. Focus on tutorial-style content for maximum engagement."
        }

    def generate_alert_message(self, topic_name: str, metric: str, value: float, threshold: float) -> str:
        """Generate a human-readable alert message."""
        return (
            f"🚨 Alert: '{topic_name}' has triggered a {metric} alert. "
            f"Current value ({value:.1f}) exceeded threshold ({threshold:.1f}). "
            f"Check your dashboard for detailed analysis."
        )