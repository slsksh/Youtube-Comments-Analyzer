import os
import re
import googleapiclient.discovery
import pandas as pd
from .comment_func import timestamp, senti
from .models import Comment, WordDict,CommentReply


class Comments:
	def __init__(self):
		os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
		self.api_service_name = "youtube"
		self.api_version = "v3"
		self.DEVELOPER_KEY = "YOUTUBE_API"       #API
		# Get WordDict from DB
		self.dbWordDict = WordDict.objects.all()
		self.youtube = googleapiclient.discovery.build(self.api_service_name, self.api_version, developerKey = self.DEVELOPER_KEY)

	# save DB
	def comment_save(self, comment, videoId, reply):
		if(reply > 0):
			self.get_comment_reply(videoId, comment['id'])
		try:
			# Get comments from DB (filtered by v_id & comment_id)
			dbComment = Comment.objects.get(video_id = videoId, comment_id = comment['id'])
			dbComment.like = comment['snippet']['likeCount']
			# if(dbComment.text != comment['snippet']['textOriginal']):
			# 	dbComment.text = comment['snippet']['textOriginal']
			# 	senti_class = senti(dbComment.text, self.dbWordDict)
			# 	dbComment.class3 = senti_class[0]
			# 	dbComment.class6 = senti_class[1]
			dbComment.save()
		except:
			text = comment['snippet']['textOriginal']
			# To lower case (Eng)
			text = text.lower()
			senti_class = senti(text, self.dbWordDict)
			comm = Comment(video_id=videoId, comment_id=comment['id'], text=comment['snippet']['textOriginal'], like=comment['snippet']['likeCount'],
				author_name=comment['snippet']['authorDisplayName'], author_image=comment['snippet']['authorProfileImageUrl'], timestamp=timestamp(text),
				class3=senti_class[0], class6=senti_class[1], published_date=comment['snippet']['publishedAt'])
			comm.save()

	def get_comment_reply(self, videoId, parentId):
		reply_comment = self.youtube.comments().list(
			part="snippet",
			parentId = parentId
		)
		try:
			reply = reply_comment.execute()
			for val in reply['items']:
				self.comment_reply_save(videoId, parentId, val['id'], val)
		except:
			return


	def comment_reply_save(self, videoId, parentId, commentId, comment):
		try:
			dbComment = CommentReply.objects.get(video_id = videoId, parent_id = parentId, comment_id = commentId)
		except:
			comm = CommentReply(video_id=videoId, parent_id=parentId, comment_id=commentId, text=comment['snippet']['textOriginal'],
				author_name=comment['snippet']['authorDisplayName'], author_image=comment['snippet']['authorProfileImageUrl'])
			comm.save()

    # Youtube API
	def get_comments(self, v_id):
		comment_lst = []
		# start youtube API
		videoID = v_id

		request = self.youtube.commentThreads().list(
			part="snippet",
			videoId = videoID
		)
		try:
			response = request.execute()
			for val in response['items']:
				comment = val['snippet']['topLevelComment']
				reply = val['snippet']['totalReplyCount']
				# save comment to DB
				self.comment_save(comment, videoID, reply)
			# if 'nextPageToken' exists
			if 'nextPageToken' in response.keys():
				token = response['nextPageToken']
				for i in range(10):
					request = self.youtube.commentThreads().list(
						part="snippet",
						videoId = videoID,
						pageToken = token
					)
					response = request.execute()
					for val in response['items']:
						comment = val['snippet']['topLevelComment']
						reply = val['snippet']['totalReplyCount']
						# save comment to DB
						self.comment_save(comment, videoID, reply)
					if 'nextPageToken' in response.keys():
						token = response['nextPageToken']
					else:
						break
		except:
			return
