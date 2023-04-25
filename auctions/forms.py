from django import forms
from .models import Bid, Comment

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

   



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)
