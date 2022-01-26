from django.conf.urls import url
from .views import main, table, update, update_abc, contract, return_docs, change_names
from .views import settings_page
from .user_views import login


urlpatterns = [
    url(r'^$', main),
    url(r'^senddata/$', table),
    url(r'^update/$', update),
    url(r'^update_abc/$', update_abc),
    url(r'^contract/$', contract),
    url(r'^return/$', return_docs),
    url(r'^change_names/$', change_names),
    url(r'^settings/$', settings_page),
    url(r'^login/$', login),
]
