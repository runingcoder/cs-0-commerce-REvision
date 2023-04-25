📚 Auction Site
Auction Site is a Django web application that allows users to create and bid on auction listings. This project was created as part of CS50's Web Programming with Python and JavaScript course.

###Features
-Three models in addition to the User model: one for auction listings, one for bids, and one for comments made on auction listings
-Create new auction listings with a title, description, starting bid, and optional image URL and category
-Active listings page to view all currently active auction listings, displaying at minimum the title, description, current price, and photo (if one exists)
-Listing page to view all details about a specific listing, including the current price for the listing, with the ability to add to Watchlist if signed in
-Ability to bid on an auction listing, with validation to ensure bid is at least as large as the starting bid and greater than any other bids that have been placed
-Ability for the creator of a listing to "close" the auction, making the highest bidder the winner of the auction and making the listing no longer active
-Ability for signed in users to add comments to the listing page and view all comments made on a specific listing
-Watchlist page for signed in users to view all listings they have added to their watchlist
-Categories page to view all listing categories and active listings within a specific category
