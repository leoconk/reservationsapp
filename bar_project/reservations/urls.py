from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tables/', views.table_list, name='table_list'),
    path('tables/<int:table_id>/reserve/', views.reserve_table, name='reserve_table'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('reservation/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),
]

