from django.conf.urls import url

from . import views, api
from .loaders import etseib, fib

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^res/js/main.js', views.mainjs, name='mainjs'),

    url(r'^api/facus', api.listFacus, name='facus'),
    # L'ordre és important, son regex i pilla la primera que passa en ordre
    url(r'^api/etseib/assigs', etseib.loadAssigs, name='etseibAssigs'),
    url(r'^api/etseib/init', etseib.loadCarreras, name='etseibInit'),
    url(r'^api/fib/init', fib.loadCarreras, name='fibInit'),
    url(r'^api/fib/assigs', fib.loadAssigs, name='fibAssigs'),
    url(r'^api/listq', api.listQ, name='listq'),
    url(r'^api/listcarr', api.listCarreras, name='listcarr'),
    url(r'^api/listassig', api.listAsigs, name='listassig'),
]
