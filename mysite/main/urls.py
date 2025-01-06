from django.urls import path

from . import views

urlpatterns = [
  path("", views.profile, name="profile"),
  path("bills", views.bills_view, name="bills"),
  path("bill_create", views.bill_create, name="bill_create"),
  path("logout/", views.logout_view, name="logout"),
]