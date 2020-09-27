from django.db import models

# Create your models here.
class Comment(models.Model):
	video_id = models.CharField(max_length=30)
	comment_id = models.CharField(max_length=30, primary_key=True)
	text = models.CharField(max_length=300)
	like = models.IntegerField()
	author_name = models.CharField(max_length=30)
	author_image = models.CharField(max_length=50)
	timestamp = models.BooleanField(default=False)
	class3 = models.IntegerField()
	class6 = models.IntegerField()
	published_date = models.DateTimeField()

	class Meta:
		ordering = ['video_id', '-like']
		unique_together = ['video_id', 'comment_id']

	def __str__(self):
		return self.video_id + '__' + self.author_name

class CommentReply(models.Model):
	video_id = models.CharField(max_length=30)
	parent_id = models.CharField(max_length=30)
	comment_id = models.CharField(max_length=60, primary_key=True)
	text = models.CharField(max_length=300)
	author_name = models.CharField(max_length=30)
	author_image = models.CharField(max_length=50)

	class Meta:
		ordering = ['video_id','parent_id']

	def __str__(self):
		return self.video_id + '__' + self.author_name

class WordDict(models.Model):
	word = models.CharField(max_length=30, primary_key=True)
	class3 = models.IntegerField()
	class6 = models.IntegerField()

	def __str__(self):
		return self.word
