from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('get_roots', views.get_roots, name='get_roots'),
	path('get_children', views.get_children, name='get_children'),
]
