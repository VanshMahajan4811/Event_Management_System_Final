"""EventManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from EM_App import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('participant', views.participant, name='participant'),
    path('event', views.event, name='event'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('api/events/', views.event_api, name='event_api'),
    path('privacypolicy', views.privacypolicy, name='privacypolicy'),
    path('contact', views.contact, name='contact'),
    path('login', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='accounts_login'),
    path('register', views.register, name='register'),
    path('flightbook', views.flightbook, name='flightbook'),
    path('my_registrations', views.my_registrations, name='my_registrations'),
    path('cancel_registration/<int:participant_id>/', views.cancel_registration, name='cancel_registration'),
]
