from django import forms
from .models import Publisher

from .models import Publisher
from .models import Review
from .models import Book
class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"
class SearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        min_length=3,
       )
    SEARCH_CHOICES = [
        ('title', 'Title'),
        ('contributor', 'Contributor'),
    ]
    search_in = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=True,
    )
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ['date_edited', 'book']
        rating = forms.IntegerField(min_value=0, max_value=5)
class BookMediaForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['cover', 'sample']