"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import oauth2_provider.views as oauth2_views

from django.conf.urls import url, include
from django.contrib import admin

from django.conf import settings
from . import views
from .api import UserViewSet, ServiceViewSet, ProviderViewSet, AccountViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'account', AccountViewSet)

oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        url(r'^applications/$', views.ApplicationCustomView.as_view(), name="list"),
        url(r'^applications/register/$', views.ApplicationCustomRegister.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', views.ApplicationCustomDetails.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', views.ApplicationCustomDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', views.ApplicationCustomUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]

urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^home/$', views.home, name="home"),
	url(r'^edit_profile/$', views.edit_profile, name="home"),
	url(r'^login/$', views.user_login, name="login"),
	url(r'^signup/$', views.signup, name="signup"),
    url(r'^api/v1/', include(router.urls)),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^o/', include(oauth2_endpoint_views, namespace="oauth2_provider")),
    url(r'^social/', include('social_django.urls', namespace='social'))
]
