from tkinter.messagebox import Message
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import AuctionListing, Bid, Category, User, WatchList
from .forms import BidForm





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

@login_required(login_url='login')
def watchlist(request):
    watchlistofUser = WatchList.objects.filter(user=request.user)
    watchlist_listings = [item.listing for item in watchlistofUser]
    context = {"listings": watchlist_listings,  "categoryMode": False}
    return render(request, "auctions/watchlist.html", context)

@login_required(login_url='login')
def CategoryList(request, category):
    categoryName = category
    category = Category.objects.get(name=categoryName)
    watchlistofCategory = AuctionListing.objects.filter(category_id=category.id)
    context = {"listings": watchlistofCategory, "categoryMode": True, "categoryName": categoryName}
    return render(request, "auctions/watchlist.html", context)

@login_required(login_url='login')
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
    
@login_required(login_url='login')    
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


@login_required(login_url='login')
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

@login_required(login_url='login')
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


@login_required(login_url='login')
def listingPage(request, listing_id):    
    listing = AuctionListing.objects.get(id=listing_id)
    num_bids = Bid.objects.filter(listing=listing).count()
    current_bid = listing.starting_bid
    bid_form = BidForm(request.POST or None)
    mybidStatus = Bid.objects.filter(user=request.user, listing=listing).exists()
    if mybidStatus:
        bid = Bid.objects.get(user=request.user, listing=listing) 
    else:
        bid = None

  
    if request.method == "POST":
        if bid_form.is_valid():
            if Bid.objects.filter(user=request.user, listing=listing).exists():
               Bid.objects.filter(user=request.user, listing=listing).delete()
            bid = bid_form.save(commit=False)
            bid.user = request.user
            bid.listing = listing
            if bid.bid > current_bid:
                bid.save()
                return redirect('listing', listing.id)
            else:
                Message.error(request, "Bid must be higher than current bid.")
                return redirect('listing', listing.id)

        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    context = {"listing": listing,  "num_bids": num_bids, "bid_form": bid_form, "mybidStatus": mybidStatus, "bid": bid}
    return render(request, "auctions/listingPage.html", context)

def mybids(request):
    bids = Bid.objects.filter(user=request.user)
    context = {"bids": bids}
    
    return render(request, "auctions/bids.html", context)