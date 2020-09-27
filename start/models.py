from django.db import models

# Create your models here.
class UserInfo(models.Model):
	usrId = models.CharField(max_length=50, primary_key=True)
	channelId = models.CharField(max_length=50)

	class Meta:
		ordering = ['usrId']

	def __str__(self):
		return self.usrId
