import json
import os
from typing import Optional

from googleapiclient.discovery import build


def get_channel_id(handle):
    youtube = build("youtube", "v3", developerKey=os.environ["YT_API_KEY"])

    # Search channels by name (handles require title match for API)
    search = youtube.channels().list(
        part="snippet,contentDetails", forHandle=handle
    )

    response = search.execute()

    print(json.dumps(response, indent=2))

    return response["items"][0]["id"]


def lookup_level_video(
    channel_id: str, level_name: str, creator_name: Optional[str] = None
) -> Optional[str]:
    youtube = build("youtube", "v3", developerKey=os.environ["YT_API_KEY"])

    search_string = level_name
    if creator_name:
        search_string = f"{level_name} by {creator_name}"

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=5,
        q=search_string,
        type="video",
    )

    try:
        response = request.execute()
        print(json.dumps(response, indent=2))

        video_id = response["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        video_title = response["items"][0]["snippet"]["title"]
        assert level_name in video_title
        if creator_name:
            assert creator_name in video_title

        return video_url

    except:
        return None


# Usage
if __name__ == "__main__":
    channel_name = "GD Archives"
    search_query = input(
        "Enter search string (e.g., 'Retray by DimaVikulov'): "
    )
    #
    channel_handle = "@gdarchives"
    # channel_id = get_channel_id(channel_handle)
    # print(channel_id)
    channel_id = "UC7AyoTC9NJarSYleR1_ZwJw"

    video_url = lookup_level_video(channel_id, search_query)

    print(video_url)
