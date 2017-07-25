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
<<<<<<< HEAD
    url(r'^logout$', views.logout),
    url(r'^sell/(?P<parameter>\d+)$', views.init_sale),
    url(r'^sell/(?P<parameter>\d+)/post_tickets$', views.post_tickets),
    url(r'^ticket_posted$', views.ticket_posted),
=======
    url(r'^post_tickets$', views.post_tickets),
>>>>>>> 2cf4488e9673167d9cee13f6f240a87e7ccf60d1
]
