from django.shortcuts import render
from django.http import HttpResponse
from .video import Comments
from .models import Comment, WordDict, CommentReply
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import mpld3
import re
from mpld3 import plugins
import googleapiclient.discovery

import matplotlib as mpl


# Create your views here.
def index(request):
	return HttpResponse("Hello, world, You're at the youtube index.")

def video(request, v_id, time):

	context = {'v_id':v_id, 'comment_url':"../comment", 'graph_url':"../graph", 'wc_url':"../wordcloud", 'time':time}
	if(time == 0):
		# Get comments from Youtube
		try:
			com = Comments()
			com.get_comments(v_id)
			print("GOT comments")
		finally:
			context['url'] = "https://www.youtube.com/embed/"+v_id+"?autoplay=1"
	else:	# Clicked Timestamp
		context['url_time'] = "https://www.youtube.com/embed/" + v_id + "?start=" + str(time) + ";autoplay=1"

	comments = []
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

	# Recommandation
	api_service_name = "youtube"
	api_version = "v3"
	DEVELOPER_KEY = "YOUTUBE_API"       #API
	try:
		youtube = googleapiclient.discovery.build(
		api_service_name, api_version, developerKey = DEVELOPER_KEY)
		r = youtube.videos().list(part="snippet",id=v_id)
		response = r.execute()
		channelId = response['items'][0]['snippet']['channelId']
		r = youtube.channels().list(part="contentDetails", id=channelId)
		response = r.execute()
	except:
		response = {'items':[]}
	for item in response['items']:
		id = item['contentDetails']['relatedPlaylists']['uploads']
		r = youtube.playlistItems().list(part="snippet, contentDetails", playlistId=id, maxResults=5)
		response = r.execute()
	videolst = []
	for item in response['items']:
		video = {}
		video_id = item['snippet']['resourceId']['videoId']
		if video_id == v_id:
			continue
		video['title'] = item['snippet']['title']
		video['id'] = video_id
		video['url'] = '/youtube/' + video_id + '/video/0'
		video['thumbnail'] = item['snippet']['thumbnails']['high']['url']
		videolst.append(video)
	context['videos'] = videolst[:4]
	return render(request, 'main.html', context)

def comment(request, v_id):
	emotion = "all"
	if request.method == 'POST':
		emotion = request.POST['emotion']
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
			query = request.GET['search']
			posts = Comment.objects.filter(video_id=v_id, text__contains=query)
			return render(request, 'comment.html',{'comments':posts})

	context = {'v_id':v_id, 'emotion':emotion}
	reply = CommentReply.objects.filter(video_id=v_id)
	rep = []
	for re in reply:
		if(re.parent_id not in rep):
			rep.append(re.parent_id)

	context['hasReply'] = rep
	context['reply'] = reply
	print(context['hasReply'])

	context['comments'] = query
	return render(request, 'comment.html', context)

def graph(request, v_id):
	percent = "all"
	if request.method == 'POST':
		percent = request.POST['percent']

	if percent != "all":
		pd_date = pd.DataFrame(columns = ['positive', 'neutral', 'negative'])
		pos_list = Comment.objects.filter(video_id=v_id, class3__gt=0)
		neu_list = Comment.objects.filter(video_id=v_id, class3=0)
		neg_list = Comment.objects.filter(video_id=v_id, class3__lt=0)

		date = []
		for data in pos_list:
			yy_mm_dd = str(data.published_date).split(' ')[0].split('-')
			date.append(yy_mm_dd[0]+yy_mm_dd[1])
		pos = pd.DataFrame({'datetime':date})
		pos = pos.groupby(['datetime']).size()


		date = []
		for data in neu_list:
			yy_mm_dd = str(data.published_date).split(' ')[0].split('-')
			date.append(yy_mm_dd[0]+yy_mm_dd[1])
		neu = pd.DataFrame({'datetime':date})
		neu = neu.groupby('datetime').size()

		date = []
		for data in neg_list:
			yy_mm_dd = str(data.published_date).split(' ')[0].split('-')
			date.append(yy_mm_dd[0]+yy_mm_dd[1])
		neg = pd.DataFrame({'datetime':date})
		neg = neg.groupby('datetime').size()

		df = pd.concat([pos, neu, neg], axis=1, keys=('positive','neutral', 'negative'))
		df = df.fillna(0)

	if percent == "true":
			# Make Percentage
			df['sum'] = df.sum(axis=1)
			df['pos'] = df['positive'] / df['sum'] * 100
			df['neu'] = df['neutral'] / df['sum'] * 100
			df['neg'] = df['negative'] / df['sum'] * 100
			df['positive'] = df['pos']
			df['neutral'] = df['neu']
			df['negative'] = df['neg']
			df = df.drop(columns=['pos', 'neu', 'neg', 'sum'])

	# Draw graph
	if percent != "all":
		if len(df.index) > 10:
			fig, ax = plt.subplots(figsize=(len(df.index)*0.5, 5))
		else:
			fig, ax = plt.subplots(figsize=(5,5))
		ax.bar(df.index, df['positive'], label='positive', bottom=df['neutral']+df['negative'], color='green')
		ax.bar(df.index, df['neutral'], label='neutral', bottom=df['negative'], color='yellow')
		ax.bar(df.index, df['negative'], label='negative', color='red')
		ax.set_xticks(df.index, minor=False)
		ax.set_xticklabels(df.index, rotation=20)
		ax.legend()
		html_fig = mpld3.fig_to_html(fig, template_type='simple')
	else:
		cnt = []
		senti_lst = ['중립', '행복', '슬픔', '놀람', '두려움', '분노']
		for i in range(6):
			cnt.append( Comment.objects.filter(video_id=v_id, class6=i).count())
		fig, ax = plt.subplots(figsize=(5,5))
		ax.pie(cnt, labels=senti_lst, labeldistance=0.5, textprops={'fontsize':17}, rotatelabels=True)
		ax.legend()

		html_fig = mpld3.fig_to_html(fig, template_type='simple', figid='fig_graph')
		print(html_fig)
	context = {'v_id':v_id, 'graph':[html_fig], 'percent':percent}

	return render(request, 'graph.html', context)

def wordcloud(request, v_id):

	stopwords = ['하지만', '그리고', '그런데', '저는', '제가', '좀', '하고', '있고', 'and', 'to', 'that',
             'they', 'it', 'he', 'she', 'is', 'but', 'of', 'her', 'be', 'this', 'so', 'really',
             'the', 'are', 'do', 'even', 'too', 'que', 'for', 'what', 'with', 'how', 'all',
             'you', 'my', 'the', 'on', 'these', 'them', 'get', 'just', 'other', 'in', 'as',
             'one', 'from', 'when', 'that', 'of', 'those', 'are', 'is', 'to', 'where', 'they',
             '저런', '이런', '합니다', '하다', '한다', '너무', '많이', '참', '정말', '그런', '나는', '내가', '있']

	emotion = "NEU"
	if request.method == 'POST':
		emotion = request.POST['senti']
	if emotion == "NEU":
		query = Comment.objects.filter(video_id=v_id, class6=0)
	elif emotion == "JOY":
		query = Comment.objects.filter(video_id=v_id, class6=1)
	elif emotion == "SAD":
		query = Comment.objects.filter(video_id=v_id, class6=2)
	elif emotion == "SUR":
		query = Comment.objects.filter(video_id=v_id, class6=3)
	elif emotion == "FEA":
		query = Comment.objects.filter(video_id=v_id, class6=4)
	else:
		query = Comment.objects.filter(video_id=v_id, class6=5)

	word_lst = []
	for doc in query:
		word_lst.append(doc.text)
	# Draw WordCloud
	try:
		wordcloud = WordCloud(
			font_path = "/usr/share/fonts/truetype/nhn-nanum/NanumGothic.ttf",
			stopwords = stopwords,
			background_color = "white",
			width = 400, height = 400,
			max_font_size=100, max_words=70).generate(''.join(word_lst))
		# pyploat
		fig, ax = plt.subplots(figsize = (6.5,6.5))
		ax.imshow(wordcloud)
		html_fig = mpld3.fig_to_html(fig, template_type='simple')
		context = {'v_id':v_id, 'wordcloud':[html_fig], 'senti': emotion}
		return render(request, 'wordcloud.html', context)
	except:				# if query == None
		return render(request, 'wordcloud.html', {'v_id':v_id, 'wordcloud':['<h2>no words</h2>'], 'senti':emotion})
