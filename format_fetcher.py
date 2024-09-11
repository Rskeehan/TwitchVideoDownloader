import yt_dlp

def fetch_formats(url):
    try:
        # Initialize yt-dlp with format extraction options
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            return formats
    except Exception as e:
        print(f"Failed to retrieve formats: {str(e)}")
        return []
