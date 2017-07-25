from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^log_reg$', views.log_reg),
    url(r'^log_out$', views.log_out),
    url(r'^acc_info$', views.acc_info),
    url(r'^sell_tickets$',views.sell_tickets),
    url(r'^registration_attempt$', views.register),
    url(r'^login_attempt$', views.login),
    url(r'^success$', views.success),
    url(r'^post_tickets$', views.post_tickets),
]
