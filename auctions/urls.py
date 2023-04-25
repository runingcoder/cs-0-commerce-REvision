from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("createlisting", views.createListing, name="createlisting"),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.CategoryList, name='categoryList'),
    path('listing/<int:listing_id>', views.listingPage, name='listing'),
    path('addtoWachList/<int:listing_id>', views.addToWatchlist, name='addtoWachList'),
    path('removefromWachList/<int:listing_id>', views.removeFromWatchlist, name='removefromWachList'),
    path('mybids', views.mybids, name='mybids'),


]
