from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import AuctionListing, Category, User, WatchList




def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def watchlist(request):
    watchlistofUser = WatchList.objects.filter(user=request.user)
    watchlist_listings = [item.listing for item in watchlistofUser]
    context = {"listings": watchlist_listings,  "categoryMode": False}
    return render(request, "auctions/watchlist.html", context)

def CategoryList(request, category):
    categoryName = category
    category = Category.objects.get(name=categoryName)
    watchlistofCategory = AuctionListing.objects.filter(category_id=category.id)
    context = {"listings": watchlistofCategory, "categoryMode": True, "categoryName": categoryName}
    return render(request, "auctions/watchlist.html", context)

def createListing(request):

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["image"]
        category_name = request.POST["category"]
        category = Category.objects.get(name=category_name)
        user = request.user
        try:
            listing = AuctionListing.objects.create(
                title=title,
                description=description,
                starting_bid=starting_bid,
                image=image,
                category=category,
                created_by=user,
            )
            listing.save()
        except IntegrityError:
            return render(
                request,
                "auctions/createListing.html",
                {"message": "Something went wrong, please try again."},
            )
        return HttpResponseRedirect(reverse("index"))
    else:
        categories = Category.objects.all()
        users = User.objects.all()
        context = {
            "categories": categories,
            "users": users,
        }
        return render(request, "auctions/createListing.html", context)
def categories(request):
    categories = Category.objects.all()
    categories_listings = []

    for category in categories:
        listings = category.category.all()
        categories_listings.append({'category': category, 'listings': listings})

    context = {'categories_listings': categories_listings}
   

    return render(request, 'auctions/categories.html', context)

def index(request):
    listings = AuctionListing.objects.all()
    watchlist_listings = []
    if request.user.is_authenticated:
        for listing in listings:
            if WatchList.objects.filter(user=request.user, listing=listing).exists():
                watchlist_listings.append(listing)
        print(watchlist_listings)        

    context = {"listings": listings, "watchlist_listings": watchlist_listings}
    return render(request, "auctions/index.html", context)


def listingPage(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    context = {"listing": listing}
    return render(request, "auctions/listingPage.html", context)

def addToWatchlist(request, listing_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=listing_id)
        user = request.user 
        try:
            if WatchList.objects.filter(user=user, listing=listing).exists():
                WatchList.objects.filter(user=user, listing=listing).delete()
            else:    
                watchlist = WatchList.objects.create(
                    user=user,
                    listing=listing,
                )
                watchlist.save()
        except IntegrityError:
            return render(  
                request,
                "auctions/listingPage.html",
                {"message": "Something went wrong, please try again."},
            )
    return HttpResponseRedirect(reverse("index"))
def removeFromWatchlist(request, listing_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=listing_id)
        user = request.user 
        try:
            if WatchList.objects.filter(user=user, listing=listing).exists():
                WatchList.objects.filter(user=user, listing=listing).delete()
        except IntegrityError:
            return render(  
                request,
                "auctions/listingPage.html",
                {"message": "Something went wrong, please try again."},
            )
    return HttpResponseRedirect(reverse("watchlist"))