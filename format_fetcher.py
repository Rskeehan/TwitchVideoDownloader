import yt_dlp

def fetch_formats(url):
    try:
        # Initialize yt-dlp with format extraction options
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # We want to return a list of available formats in a user-friendly way
            available_formats = []
            for f in formats:
                format_note = f.get('format_note', 'Unknown')
                resolution = f.get('height', 'Unknown')  # Video resolution
                framerate = f.get('fps', 'Unknown')  # Video framerate
                format_id = f.get('format_id')  # Format ID used for downloading

                # Append formatted string describing the resolution and framerate
                available_formats.append({
                    'format_note': format_note,
                    'resolution': resolution,
                    'framerate': framerate,
                    'format_id': format_id
                })
            
            return available_formats
    except Exception as e:
        print(f"Failed to retrieve formats: {str(e)}")
        return []
