import json
import time
from googleapiclient.discovery import build
from tqdm import tqdm

# CONFIGURATION


API_KEY = "AIzaSyC29a67D7K95M3NUyuMKgPvO9IM_sYdIQg"

QUERY = "Apple iPhone OR Apple MacBook OR Apple iOS OR Apple event"

MAX_VIDEOS = 50          # increase later 
MAX_COMMENTS = 50        # per video

OUTPUT_FILE = "youtube_raw.json"


# INIT YOUTUBE CLIENT

youtube = build("youtube", "v3", developerKey=API_KEY)



# GET VIDEOS

def get_videos(query, max_results):
    videos = []

    request = youtube.search().list(
        q=query,
        part="id,snippet",
        type="video",
        maxResults=max_results
    )

    response = request.execute()

    for item in response["items"]:
        video_id = item["id"]["videoId"]

        videos.append({
            "video_id": video_id,
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "published_at": item["snippet"]["publishedAt"],
            "channel_title": item["snippet"]["channelTitle"]
        })

    return videos



# GET COMMENTS


def get_comments(video_id, max_comments):
    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_comments,
            textFormat="plainText"
        )

        response = request.execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({
                "text": comment["textDisplay"],
                "author": comment["authorDisplayName"],
                "likes": comment["likeCount"],
                "published_at": comment["publishedAt"]
            })

    except Exception as e:
        # comments disabled or API limit reached
        pass

    return comments



# MAIN PIPELINE


def collect_data():
    raw_data = []

    print("Fetching videos...")
    videos = get_videos(QUERY, MAX_VIDEOS)

    print(f"Total videos fetched: {len(videos)}")

    for video in tqdm(videos):
        video_id = video["video_id"]

        comments = get_comments(video_id, MAX_COMMENTS)

        raw_data.append({
            "video": video,
            "comments": comments
        })

        time.sleep(0.2)  # avoids API quota spikes

    return raw_data



# SAVE TO FILE


def save_to_json(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {OUTPUT_FILE}")



# RUN PIPELINE


if __name__ == "__main__":
    data = collect_data()
    save_to_json(data)