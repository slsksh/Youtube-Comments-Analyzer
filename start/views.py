from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from allauth import socialaccount
import requests
from isodate import parse_duration
from youtube.models import Comment
from .creator_list import creator_list
from youtube.video import Comments
from .models import UserInfo
import re

def start(request):
	videos = []
	if request.method == 'POST':
		search_url = 'https://www.googleapis.com/youtube/v3/search'
		video_url = 'https://www.googleapis.com/youtube/v3/videos'

		search_params = {
			'part' : 'snippet',
			'q' : request.POST['search'],
			'key' : settings.YOUTUBE_DATA_API_KEY,
			'maxResults': 18,
			'type' : 'video'
		}

		# start Youtube API
		r = requests.get(search_url, params=search_params)
		print(r.json())
		results = r.json()['items']

		video_ids = []
		for result in results:
			video_ids.append(result['id']['videoId'])

		# Get Video Info
		video_params = {
			'key' : settings.YOUTUBE_DATA_API_KEY,
			'part' : 'snippet, contentDetails',
			'id' : ','.join(video_ids),
			'maxResults' : 18
		}

		r = requests.get(video_url, params=video_params)
		results = r.json()['items']
		for result in results:
			video_data = {
				'title': result['snippet']['title'],
				'id': result['id'],
				'url': '../youtube/'+ result["id"] + '/video/0',
				'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
				'thumbnail': result['snippet']['thumbnails']['high']['url']
			}

			videos.append(video_data)

	context = {
	    'videos': videos
	}

	return render(request, 'start_page.html', context)

def user_info(request, user, user_id):
	context = {'user_name':user, 'user_id':user_id}
	channel = ""
	cre = creator_list()
	try:
		query = UserInfo.objects.get(usrId=user_id)
		channel = query.channelId
		if request.method == 'POST':
			channel = request.POST['ChannelId']
			query.channelId = channel
			query.save()
	except:
		if request.method == 'POST':
			channel = request.POST['ChannelId']
			query = UserInfo(usrId=user_id, channelId=channel)
			query.save()
	finally:
		context['channel'] = channel
		return render(request, 'user_info.html', context)

def creator(request, user, user_id):
	context = {'user_id':user_id, 'user_name':user}
	try:
		query = UserInfo.objects.get(usrId=user_id)
		print(query)
	except:
		channel = ""
		context['channel'] = channel
		return redirect("http://BASE_URL/userinfo/"+user+"/" +user_id)
	else:
		cre = creator_list()
		# Get Youtube API results
		response = cre.video_list(query.channelId)
		videolst = []
		for item in response['items']:
			video = {}
			video['title'] = item['snippet']['title']
			video['id'] = item['snippet']['resourceId']['videoId']
			video['url'] = '../' + user + "/" + video['id'] + "/video/0"
			video['thumbnail'] = item['snippet']['thumbnails']['high']['url']
			videolst.append(video)
		context['videos'] = videolst
		return render(request, 'creator.html', context)

def creator_video(request, user, v_id, time):
	context = {'user_id' : user, 'v_id':v_id, 'comment_url':"../comment", 'graph_url':"../../../../youtube/"+v_id+"/graph", 'wc_url':"../../../../youtube/"+v_id+"/wordcloud", 'time':time}
	if(time == 0):
		# Get comments from Youtube
		try:
			com = Comments()
			com.get_comments(v_id)
		finally:
			context['url'] = "https://www.youtube.com/embed/"+v_id
	else:	# Clicked Timestamp
		context['url_time'] = "https://www.youtube.com/embed/" + v_id + "?start=" + str(time) + ";autoplay=1"
	# Get comments with TimeStamp == True
	query = Comment.objects.filter(video_id=v_id, timestamp=True).order_by('-like')[:5]
	# Timestamp linked
	for com in query:
		doc = com.text
		span_lst = []
		time_lst = []
		regex = re.compile(r'\d*:\d\d')
		matchobj = regex.finditer(doc)
		idx = 0
		for i in matchobj:
			span_lst.append(i.span())
			times = i.group().split(':')
			time_lst.append(int(times[0])*60 + int(times[1]))
			idx = idx + 1

		for span in span_lst[::-1]:
			idx = idx - 1
			doc = doc[:span[0]] + "<a href='./" + str(time_lst[idx]) + "'>" + doc[span[0]:span[1]] + "</a>" + doc[span[1]:]
		com.text = [doc]
	context['comments'] = query
	return render(request, 'main.html', context)

def creator_comment(request, user, v_id):
	emotion = "all"
	if request.method == 'POST':
		emotion = request.POST['emotion']
	# Get comments from DB (filtered by v_id & class3)
	if emotion == "all":
		query = Comment.objects.filter(video_id=v_id)
	elif emotion == "pos":
		query = Comment.objects.filter(video_id=v_id, class3__gt=0)
	elif emotion == "0":
		query = Comment.objects.filter(video_id=v_id, class3=0)
	else:
		query = Comment.objects.filter(video_id=v_id, class3__lt=0)
	query = query[:500]
	if request.method == 'GET':
		if 'search' in request.GET:
			query = Comment.objects.filter(video_id=v_id, text__contains=request.GET['search'])

	context = {'v_id':v_id, 'comments':query, 'emotion':emotion}
	return render(request, 'creator_comment.html', context)

def change(request, user, v_id, c_id):
	# Change class3 by creator (modal)
	cmt = Comment.objects.get(video_id=v_id, comment_id=c_id)
	print(request.GET)
	if '3sent' in request.GET:
		print(request.GET['3sent'])
		if request.GET['3sent'] == "0":
			cmt.class3 = 5
		elif request.GET['3sent'] == "1":
			cmt.class3 = 0
		else:
			cmt.class3 = -5
		cmt.save()
	print(cmt.class3)
	if '6sent' in request.GET:
		cmt.class6 = int(request.GET['6sent'])
		cmt.save()

	return redirect('http://BASE_URL/creator/'+user+"/"+v_id+"/comment")
