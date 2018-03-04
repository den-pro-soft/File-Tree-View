from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('get_roots', views.get_roots, name='get_roots'),
	path('get_children', views.get_children, name='get_children'),
	path('get_listdata', views.get_listdata, name='get_listdata'),
	path('get_all_files', views.get_all_files, name='get_all_files'),
]
