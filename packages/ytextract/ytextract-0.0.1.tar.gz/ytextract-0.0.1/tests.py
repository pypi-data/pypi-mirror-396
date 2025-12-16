import ytextract

TEST_VIDEO_URL = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"

print("Download a Video from URL:")
print(ytextract.download_video(url=TEST_VIDEO_URL))
print("Download Captions for Video:")
print(ytextract.download_captions(url=TEST_VIDEO_URL))
