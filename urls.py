from django.conf.urls import url
from .views import main, table, update, update_abc,contract


urlpatterns = [
    url(r'^$', main),
    url(r'^senddata/$', table),
    url(r'^update/$', update),
    url(r'^update_abc/$', update_abc),
    url(r'^contract/$', contract),
]

# urlpatterns = [
#     url(r'^(\d+)$', userpage),
#     url(r'^login/$', login),
#     url(r'^logout/$', logout),
#     url(r'^registration/$', registration),
#     url(r'^delete/(\d+)/$', delete),
#     url(r'^edit/(\d+)/$', edit),
# ]