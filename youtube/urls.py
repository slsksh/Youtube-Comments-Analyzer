from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:v_id>/video/<int:time>', views.video, name='video'),
    path('<str:v_id>/comment', views.comment, name='comment'),
    path('<str:v_id>/graph', views.graph, name='graph'),
    path('<str:v_id>/wordcloud', views.wordcloud, name='graph')
]
