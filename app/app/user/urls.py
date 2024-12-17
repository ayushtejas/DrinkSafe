from django.urls import path

from user import views

app_name='user'

urlpatterns = [
    path('create/', views.UserView.as_view(), name='create'),
    path('login/', views.CreateTokenView.as_view(), name='login'),
    path('me/', views.UpdateUserView.as_view(), name='update')
]
