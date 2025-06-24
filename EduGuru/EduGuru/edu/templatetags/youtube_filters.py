from django import template
import re

register = template.Library()

@register.filter
def extract_youtube_id(value):
    """
    Extracts the video_id from a YouTube URL.
    Handles URLs of type:
    - https://www.youtube.com/watch?v=...
    - https://youtu.be/...
    """
    if not value:
        return ""
    regex = (
        r"(?:https?://)?(?:www\.)?"
        r"(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)"
        r"([^\"&?/\s]{11})"
    )
    match = re.search(regex, value)
    return match.group(1) if match else ""
