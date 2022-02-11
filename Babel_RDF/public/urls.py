from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mangas/page/<int:page>', views.manga_list, name='manga_list'),
    path('manga/<str:name>', views.manga_details, name='manga_details'),
    path('auteurs', views.auteurs_list, name='auteurs_list'),
    path('auteur/<str:name>', views.auteur_details, name='auteur_details'),
]