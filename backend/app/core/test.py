from youtube_transcript_api import YouTubeTranscriptApi

video_id = "m_xJlJ9nE2U" # The Sora video you sent

print(f"Testing video: {video_id}...")

try:
    # Try the modern method
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(['en'])
    data = transcript.fetch()
    print("SUCCESS! Found transcript (New Method):")
    print(" ".join([t['text'] for t in data])[:100] + "...")
except Exception as e:
    print(f"New method failed: {e}")
    try:
        # Try the classic method
        data = YouTubeTranscriptApi.get_transcript(video_id)
        print("SUCCESS! Found transcript (Classic Method):")
        print(" ".join([t['text'] for t in data])[:100] + "...")
    except Exception as e2:
        print(f"Classic method failed: {e2}")