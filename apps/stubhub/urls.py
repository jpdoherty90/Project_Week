from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^log_reg$', views.log_reg),
    url(r'^acc_info$', views.acc_info),
    url(r'^registration_attempt$', views.register),
    url(r'^login_attempt$', views.login),
    url(r'^success$', views.success),
    url(r'^log_out$', views.log_out),
    url(r'^sell/(?P<parameter>\d+)$', views.init_sale),
    url(r'^sell/(?P<parameter>\d+)/post_tickets$', views.post_tickets),
    url(r'^ticket_posted/(?P<parameter>\d+)$', views.ticket_posted),
    url(r'^buy/(?P<parameter>\d+)$', views.buy_tix),
    url(r'^confirmation$', views.cart),
    url(r'^add_to_cart$', views.add_to_cart),
    url(r'^cart$', views.cart),
    url(r'^purchase$', views.purchase),
    url(r'^search$', views.search_results),  
    url(r'^process_search$', views.process_search), 
    url(r'^event/(?P<parameter>\d+)$', views.show_event),
]
