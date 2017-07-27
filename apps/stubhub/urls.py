from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^log_reg$', views.log_reg),
    url(r'^acc_info/(?P<parameter>\d+)$', views.acc_info),
    url(r'^registration_attempt$', views.register),
    url(r'^login_attempt$', views.login),
    url(r'^log_out$', views.log_out),
    url(r'^sell_tickets_search$', views.sell_search),
    url(r'^sell/(?P<parameter>\d+)$', views.init_sale),
    url(r'^sell/(?P<parameter>\d+)/post_tickets$', views.post_tickets),
    url(r'^ticket_posted/(?P<parameter>\d+)$', views.ticket_posted),
    url(r'^buy/(?P<parameter>\d+)$', views.buy_tix),
    url(r'^confirmation$', views.cart),
    url(r'^add_to_cart$', views.add_to_cart),
    url(r'^remove_from_cart/(?P<parameter>\d+)$', views.remove_from_cart),
    url(r'^check_out$', views.check_out),
    url(r'^cart$', views.cart),
    url(r'^payment_shipping$', views.payment_shipping),
    url(r'^purchase$', views.purchase),
    url(r'^order_review$', views.order_review),
    url(r'^order_confirmation$', views.order_confirmation),
    url(r'^search$', views.search_results),  
    url(r'^process_search$', views.process_search), 
    url(r'^event/(?P<parameter>\d+)$', views.show_event),
]
