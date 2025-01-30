from django.urls import path
from Demo import views

urlpatterns = [
    path('formtoken', views.formtoken, name='formtoken'),
    path('validate', views.validate, name='validate'),
    path('ipn', views.ipn, name='ipn')
]