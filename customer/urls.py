from django.urls import path
from . import views

urlpatterns = [
 path("add/", views.add_customer, name="add_customer"),
    path("list/", views.customer_list, name="customer_list"),
     path('users/', views.user_list, name='user_list'),
     path('index', views.index, name='index'),
     path('users/', views.user_list, name='user_list'),
      path("customer-list/", views.admincustomer_list, name="customers_list"),
       path("customers-update/<int:pk>/update/", views.adminupdate_customer, name="updates_customer"),
     path('users-edit/<int:user_id>/edit/', views.edit_user, name='edit_user'),
      path('users_disable/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
     path("delete/<int:pk>/", views.delete_customer, name="delete_customer"),
     path("customers/<int:pk>/update/", views.update_customer, name="update_customer"),
     path("deletecustomer/<int:pk>/", views.admindelete_customer, name="deletes_customer"),
    
]