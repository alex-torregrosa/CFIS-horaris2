from django.conf.urls import url

from . import views, api

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^res/js/main.js', views.mainjs, name='mainjs'),

    url(r'^api/facus', api.listFacus, name='facus'),
    url(r'^api/genetseibassig', api.loadEtseibAssigs, name='etseibGenAssig'),
    url(r'^api/genetseib', api.loadCarrerasEtseib, name='etseibGen'),
    url(r'^api/listq', api.listQ, name='listq'),
    url(r'^api/listcarr', api.listCarreras, name='listcarr'),
    url(r'^api/listassig', api.listAsigs, name='listassig'),
]
