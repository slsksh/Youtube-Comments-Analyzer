import googleapiclient.discovery

class creator_list:
	def __init__(self):
		self.api_service_name = "youtube"
		self.api_version = "v3"
		self.DEVELOPER_KEY = "YOUTUBE_API"       #API
		self.youtube = googleapiclient.discovery.build(self.api_service_name, self.api_version, developerKey = self.DEVELOPER_KEY)

	def video_list(self,channelId):
		r = self.youtube.channels().list(part="contentDetails", id=channelId)
		response = r.execute()
		print(response)
		for item in response['items']:
			id = item['contentDetails']['relatedPlaylists']['uploads']
			r = self.youtube.playlistItems().list(part="snippet, contentDetails", playlistId=id, maxResults=20)
			response = r.execute()

		return response
