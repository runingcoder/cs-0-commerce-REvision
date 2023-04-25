from tkinter.messagebox import Message
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Max
from django.db.models import Q




from .models import *
from .forms import BidForm, CommentForm


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


@login_required(login_url="login")
def watchlist(request):
    watchlistofUser = WatchList.objects.filter(user=request.user)
    print(watchlistofUser)
    watchlist_listings = [item.listing for item in watchlistofUser]
    context = {"listings": watchlist_listings}
    return render(request, "auctions/watchlist.html", context)


@login_required(login_url="login")
def CategoryList(request, category):
    categoryName = category
    category = Category.objects.get(name=categoryName)
    watchlistofCategory = AuctionListing.objects.filter(category_id=category.id)
    context = {"listings": watchlistofCategory, "categoryName": categoryName}
    return render(request, "auctions/categoryList.html", context)


@login_required(login_url="login")
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


@login_required(login_url="login")
def categories(request):
    categories = Category.objects.all()
    categories_listings = []

    for category in categories:
        listings = category.category.all()
        categories_listings.append({"category": category, "listings": listings})

    context = {"categories_listings": categories_listings}

    return render(request, "auctions/categories.html", context)


def index(request):
    # listings whose created_by is not the current user
    listings = AuctionListing.objects.exclude(Q(created_by=request.user.id) | Q(active=False))
    watchlist_listings = []
    if request.user.is_authenticated:
        for listing in listings:
            if WatchList.objects.filter(user=request.user, listing=listing).exists():
                watchlist_listings.append(listing)
        print(watchlist_listings)

    context = {"listings": listings, "watchlist_listings": watchlist_listings}
    return render(request, "auctions/index.html", context)


@login_required(login_url="login")
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


@login_required(login_url="login")
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


@login_required(login_url="login")
def listingPage(request, listing_id, watchListmode="False"):

    listing = AuctionListing.objects.get(id=listing_id)
    comments = Comment.objects.filter(listing=listing)
    comment_form = CommentForm(request.POST or None)
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
           
            bid = bid_form.save(commit=False)
            bid.user = request.user
            bid.listing = listing
            if bid.bid >= current_bid:
                if Bid.objects.filter(user=request.user, listing=listing).exists():
                     Bid.objects.filter(user=request.user, listing=listing).delete()
                bid.save()
                messages.success(request, 'Your bid has been submitted')
                return redirect("listing", listing.id,'True')
            else:
                messages.error(request, f'Bid must be higher than the current bid of {current_bid}')
                return redirect("listing", listing.id,'True')
                
               
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.save()
            return redirect("listing", listing.id,'True')


        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    if watchListmode == 'True':
        watchListmode = True
    else:
        watchListmode = False
    context = {
        "comment_form": comment_form,
        "comments": comments,
        "listing": listing,
        "num_bids": num_bids,
        "bid_form": bid_form,
        "watchListmode": watchListmode,
        "mybidStatus": mybidStatus,
        "bid": bid,
    }
    return render(request, "auctions/listingPage.html", context)


@login_required(login_url="login")
def mybids(request):
    bids = Bid.objects.filter(user=request.user)
    context = {"bids": bids}

    return render(request, "auctions/bids.html", context)


@login_required(login_url="login")
def myListings(request):
    listings = AuctionListing.objects.filter(created_by=request.user)
    context = {"listings": listings}
    return render(request, "auctions/mylistings.html", context)

def closedListings(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    listing.active = False
    listing.save()
    listing = AuctionListing.objects.get(id=listing_id)
    # get the highest bid for the listing
    if not Bid.objects.filter(listing=listing).exists():
        listing.winner_id = None
        listing.save()
        return HttpResponseRedirect(reverse("myListings"))
    highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))['bid__max']
    print(highest_bid)
    # get the user(s) with the highest bid
    winners = Bid.objects.filter(listing=listing, bid=highest_bid).values_list('user', flat=True)
    print(winners[0])
    # set the winner field on the listing to the user with the highest bid (assuming there is only one winner)
    listing.winner_id = winners[0]
    listing.save()
    
    return HttpResponseRedirect(reverse("myListings"))