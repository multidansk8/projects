from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment

#Categories available
categories = [
    "Cleaning",
    "Electronics",
    "Sports",
    "Educational",
    "Outdoors",
    "Household",
    "Style",
    "Beauty",
    "Health",
    "Gaming",
    "Music",
    "Books",
    "Recreational",
    "Miscellaneous"
]


def index(request):
    #We get the listings with the active field (defined in Listing model) set to true
    listings = Listing.objects.filter(active=True)
    Title = "Active Listings"
    #We get the length of the iterable listings to determine wether there are listings to display or not
    #In the event of the length being 0 we display a message in the index html templare
    length = len(listings)

    return render(request, "auctions/index.html", {
        "listings": listings,
        "Title": Title,
        "len": length
    })


def listing(request, listing_id):
    userId = request.session.get("username", 1)

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        # inWatchlist is a value that will allow us to determine whether a listing is in the watchlist of
        # the signed in user (userId), if the user is inside the watchlist attribute of our listing it means
        # that the user has added this listing to her watchlist
        inWatchlist = User.objects.get(pk=userId) in listing.watchlist.all()

        #We check several POST forms inside the same html template
        #and work with whichever was activated by the user

        if "commentsSub" in request.POST:

            #We get a comment from the form
            comment = request.POST["comment"]

            #We save such comment to our database
            Comment(comment=comment, listing=listing, commenter=User.objects.get(pk=request.session["username"])).save()

            #We get the bids associated with the listing at hand
            listingBid = Bid.objects.filter(listing=listing)

            return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(pk=listing_id),
                "bidNo": len(listingBid),
                "highestBid": listingBid.last(),
                "comments": Comment.objects.filter(listing=listing),
                "commentLen": len(Comment.objects.filter(listing=listing)),
                "inWatchlist": inWatchlist
            })

        elif "bidButton" in request.POST:
            bid = request.POST["bid"]

            #We perform logic to determine whether the bid placed on the form fulfills the constraints,
            #Namely preventing a bid from being placed if it is less than or equal to the starting bid or
            #current highest bid

            if float(bid) > listing.price:

                #If the constraint is fulfilled we save the bid to our database
                Bid(amount=float(bid), listing=listing, bidder=User.objects.get(pk=request.session["username"])).save()

                #We make the price of the listing at hand the bid previously placed
                Listing.objects.filter(pk=listing_id).update(price=float(bid))

                #We get all the bids associated with this listing. Since the price will be
                #always updating given a bid fulfilling the constraints, we know that the last object
                #inside the Bid model will always be the highest bid on a particular listing

                listingBid = Bid.objects.filter(listing=listing)

                #We perform an exception to check whether there are comments on the listing
                #If a comment exists we can display them through the 'comments' key. Otherwise,
                #The exception will pass an empty list in order to only display a message notifying of the
                #lack of comments
                try:
                    comments = Comment.objects.filter(listing=listing)
                    return render(request, "auctions/listing.html", {
                        "listing": Listing.objects.get(pk=listing_id),
                        "bidNo": len(listingBid),
                        "highestBid": listingBid.last(),
                        "comments": comments,
                        "commentLen": len(comments),
                        "inWatchlist": inWatchlist
                    })
                except NameError:
                    return render(request, "auctions/listing.html", {
                        "listing": Listing.objects.get(pk=listing_id),
                        "bidNo": len(listingBid),
                        "highestBid": listingBid.last(),
                        "comments": [],
                        "commentLen": 0,
                        "inWatchlist": inWatchlist
                    })
            else:
                #If the bid does not fulfill the constraints we display an error page.
                errorMessage = f"Your bid must be greater than the starting price or the current highest bid."
                return render(request, "auctions/error.html", {
                    "errorMessage": errorMessage
                })

        #If the POST form activated by the user was the one for closing the listing, we go ahead and
        #set active to false on the listing at hand in order to close it
        else:
            Listing.objects.filter(pk=listing_id).update(active=False)
            return HttpResponseRedirect(reverse("index"))

    #We check whether the listing exists by using a try/except structure
    try:

        listing = Listing.objects.get(pk=listing_id)

        #Same logic as explained above
        inWatchlist = User.objects.get(pk=userId) in listing.watchlist.all()

        #We get the bids associated with the listing in order to get the number of bids
        bids = Bid.objects.filter(listing=listing)

        #We render the html template with the current information
        if len(bids) == 0:
            # We create a try and except block to check for comments associated with the listing at hand.
            # If no comments exist then we proceed with the except block.
            try:
                comments = Comment.objects.filter(listing=listing)
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bidNo": len(bids),
                    "highestBid": Bid.objects.filter(listing=listing).last(),
                    "comments": comments,
                    "commentLen": len(comments),
                    "inWatchlist": inWatchlist
                })
            except NameError:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bidNo": len(bids),
                    "highestBid": Bid.objects.filter(listing=listing).last(),
                    "comments": [],
                    "commentLen": 0,
                    "inWatchlist": inWatchlist
                })

        #We update the price of the listing to the highest current bid available for the listing in order to
        #ensure that the highest bid is in fact displayed with the listing
        maxBid = bids.last().amount
        Listing.objects.filter(pk=listing_id).update(price=maxBid)
        listingBid = Bid.objects.filter(listing=listing)

        #Same logic as above
        try:
            comments = Comment.objects.filter(listing=listing)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidNo": len(listingBid),
                "highestBid": listingBid.last(),
                "comments": comments,
                "commentLen": len(comments),
                "inWatchlist": inWatchlist
            })
        except NameError:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidNo": len(listingBid),
                "highestBid": listingBid.last(),
                "comments": [],
                "commentLen": 0,
                "inWatchlist": inWatchlist
            })
    except Listing.DoesNotExist:
        #We display an error page with a message specifying error
        errorMessage = f"A listing with id {listing_id} does not exist"
        return render(request, "auctions/error.html", {
            "errorMessage": errorMessage
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session["username"] = user.id
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    del request.session["username"]
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        request.session["username"] = user.id
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def category_view(request, category):
    #This category view will dislay all listings with a given category and active status
    listings = Listing.objects.filter(category=category, active=True)
    Title = f"Results For Category: {category}"
    length = len(listings)
    name = request.session.get('username', None)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "Title": Title,
        "name": name,
        "len": length
    })


def categories_view(request):
    #This simple view displays an html list of all available categories linked to their correspinding active listings
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


@login_required
def watchlist(request):
    #This view was created to manage the watchlist mechanism
    if request.method == "POST":
        listing_id = int(request.POST["listingToAdd"])

        #We develop the mechanism to remove from the watchlist
        if "removeFrom" in request.POST:

            #We get our listing instance, then we determine the user whose watchlist
            #needs to be deprived of our listing instance, and we remove the user from
            #the watchlist attribute of our current listing
            listingOfInterest = Listing.objects.get(pk=listing_id)
            userToRemove = User.objects.get(pk=request.session["username"])
            listingOfInterest.watchlist.remove(userToRemove)
            return HttpResponseRedirect(reverse("index"))

        #We develop the logic to add to the watchlist
        elif request.POST["watch"] == "yes":

            #We get our listing of interest and add the logged in user to the watchlist
            #attribute of our listing in order to take the listing to the user's watchlist.
            listing = Listing.objects.get(pk=listing_id)
            listing.watchlist.add(request.session["username"])

            #Here we perform similar logic as in the listing view
            listingBid = Bid.objects.filter(listing=listing)
            try:
                comments = Comment.objects.filter(listing=listing)
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bidNo": len(listingBid),
                    "highestBid": listingBid.last(),
                    "comments": comments,
                    "commentLen": len(comments),
                    "inWatchlist": True
                })
            except NameError:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bidNo": len(listingBid),
                    "highestBid": listingBid.last(),
                    "comments": [],
                    "commentLen": 0,
                    "inWatchlist": True
                })


    #We display the list of watchlisted listings inside the watchlist page
    #of the logged in user.
    user_id = request.session["username"]
    user = User.objects.get(pk=user_id)
    listings = user.watchlist.all()
    Title = f"Watchlist"
    length = len(listings)
    name = request.session.get('username', None)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "Title": Title,
        "name": name,
        "len": length
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        #We retrieve all the data from the html form in order to add our new listing to the database
        title = request.POST["title"]
        price = request.POST["price"]
        category = request.POST["category"]
        description = request.POST["description"]
        image_url = request.POST["imgURL"]

        #We check whether the image_url input box is empty so that we allow users to choose
        #whether to use images for their listings or not
        if image_url == "":
            Listing(name=title, description=description, price=price, author=User.objects.get(pk=request.session["username"]), category=category).save()
        else:
            Listing(name=title, description=description, price=price, author=User.objects.get(pk=request.session["username"]), category=category, image=image_url).save()


        #We get the listing we have just created and display it through the listing.html template
        listing_1 = Listing.objects.filter(author=User.objects.get(pk=request.session["username"])).last()
        listingBid_1 = Bid.objects.filter(listing=listing_1)

        #Same logic this this try/except block as explained in previous views
        try:
            comments = Comment.objects.filter(listing=listing_1)
            return render(request, "auctions/listing.html", {
                "listing": listing_1,
                "bidNo": len(listingBid_1),
                "highestBid": listingBid_1.last(),
                "comments": comments,
                "commentLen": len(comments),
            })
        except NameError:
            return render(request, "auctions/listing.html", {
                "listing": listing_1,
                "bidNo": len(listingBid_1),
                "highestBid": listingBid_1.last(),
                "comments": [],
                "commentLen": 0
            })

    #Given the GET method we just display a page to allow users to create their own listings
    return render(request, "auctions/create_listing.html", {
        "categories": categories
    })


def closed_view(request):
    #An additional view to keep track of closed listings.
    #We just filter out listings with their active field
    #set to true (active listings) and display as usual.
    listings = Listing.objects.filter(active=False)
    Title = "Closed Listings"
    name = request.session.get('username', None)
    length = len(listings)

    return render(request, "auctions/index.html", {
        "listings": listings,
        "Title": Title,
        "name": name,
        "len": length
    })