from django import forms
from .models import Bid, Comment

class BidForm(forms.ModelForm):
    def __init__(self, *args, listing=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing = listing

    class Meta:
        model = Bid
        fields = ['bid']

    def clean_bid_value(self):
        bid_value = self.cleaned_data['bid_value']
        min_bid_value = self.listing.starting_bid
        if bid_value < min_bid_value:
            raise forms.ValidationError(f'The bid value must be greater than or equal to {min_bid_value}')
        return bid_value


   



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)
