from django.urls import path

from . import views

urlpatterns = [
  path("", views.profile, name="profile"),
  path("logout/", views.logout_view, name="logout"),
  path("bills", views.bills_view, name="bills"),
  path("bill_create", views.bill_create, name="bill_create"),
  path('bill/<int:bill_id>/', views.bill_detail, name='bill_detail'),
]