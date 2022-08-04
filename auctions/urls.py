from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed", views.closed_view, name="closed"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("categories", views.categories_view, name="categories"),
    path("categories/<str:category>", views.category_view, name="category"),
    path("create_listing", views.create_listing, name="create_listing")
]
