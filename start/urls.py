from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import start
from . import views

urlpatterns = [
	path('', views.start, name='start'),
	path('userinfo/<str:user>/<str:user_id>', views.user_info, name='user_info'),
	path('creator/<str:user>/<str:user_id>', views.creator, name='creator'),
	path('creator/<str:user>/<str:v_id>/video/<int:time>', views.creator_video, name='video'),
	path('creator/<str:user>/<str:v_id>/comment', views.creator_comment, name='comment'),
	path('creator/<str:user>/<str:v_id>/change/<str:c_id>', views.change, name='change')
]
