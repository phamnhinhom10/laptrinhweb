from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review, Contributor, Publisher
from .utils import average_rating
from django.contrib import messages
from .forms import PublisherForm, SearchForm, ReviewForm
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .serializers import ContributorSerializer
from .forms import BookMediaForm
from io import BytesIO
from PIL import Image
from django.core.files.images import ImageFile
from django.contrib.auth.decorators import (login_required,
user_passes_test)
from django.core.exceptions import PermissionDenied
def index(request):
  return render(request, "base.html")


def book_search(request):
    form = SearchForm(request.GET or None)
    books = []
    search_text = ""

    if form.is_valid():
        search_text = form.cleaned_data.get('search', '')
        search_in = form.cleaned_data.get('search_in', 'title')  # Giá trị mặc định là 'title'

        if search_text:
            if search_in == 'title':
                books = Book.objects.filter(title__icontains=search_text)
            elif search_in == 'contributor':
                first_names_results = Book.objects.filter(contributors__first_names__icontains=search_text)
                last_names_results = Book.objects.filter(contributors__last_names__icontains=search_text)
                books = first_names_results | last_names_results
                books = books.distinct()  # Loại bỏ trùng lặp
    return render(request, 'reviews/search_results.html', {
        'form': form,
        'books': books,
        'search_text': search_text,
    })

def book_list(request):
  books = Book.objects.all()
  book_list = []
  for book in books:
   reviews = book.review_set.all()
   if reviews:
      book_rating = average_rating([review.rating for
review in reviews])
      number_of_reviews = len(reviews)
   else:
      book_rating = None
      number_of_reviews = 0
   book_list.append({'book': book,
                     'book_rating': book_rating,
                     'number_of_reviews':
number_of_reviews})
  context = {
       'book_list': book_list
  }
  return render(request, 'reviews/book_list.html', context)

def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    reviews = Review.objects.filter(book=book)
    return render(request, 'reviews/book_detail.html', {'book': book, 'reviews': reviews})


def is_staff_user(user):
 return user.is_staff
@user_passes_test(is_staff_user)
def publisher_edit(request, pk=None):
        if pk is not None:
            publisher = get_object_or_404(Publisher, pk=pk)
        else:
            publisher = None

        if request.method == "POST":
            form = PublisherForm(request.POST, instance=publisher)
            if form.is_valid():
                updated_publisher = form.save()
                if publisher is None:
                    messages.success(request, "Publisher '{}' was created.".format(updated_publisher.name))
                else:
                    messages.success(request, "Publisher '{}' was updated.".format(updated_publisher.name))
                return redirect("publisher_edit", updated_publisher.pk)
        else:
            form = PublisherForm(instance=publisher)
        return render(request, "reviews/instance-form.html", { "form": form, 'instance': publisher,'model_type': 'Publisher'})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Review, Book
from .forms import ReviewForm
from django.utils import timezone

@login_required
def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)
    if review_pk is not None:
        review = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
        user = request.user
        if not user.is_staff and review.creator.id != user.id:
            raise PermissionDenied
    else:
        review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            if review_pk:
                review.date_edited = timezone.now()  # Chỉnh sửa thời gian
            review.save()
            # Thông báo thành công
            messages.success(request,
                             f"Review for '{book.title} ({book.isbn})' {'updated' if review_pk else 'created'}")
            return redirect('book_detail', id=book.pk)  # Đổi book_pk thành id
    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/instance-form.html", {
        "form": form,
        "instance": review,
        "model_type": "Review",
        "related_model_type": "Book",
        "related_instance": book,
        "book_title": book.title,
        "creator": review.creator.username if review else "Your Username"
    })
class ContributorView(ListAPIView):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

@login_required
def book_media(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookMediaForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            book = form.save(False)

            cover = form.cleaned_data.get("cover")

            if cover and not hasattr(cover, "path"):
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = ImageFile(image_data)
                book.cover.save(cover.name, image_file)
            book.save()
            messages.success(
                request, 'Book "{}" was successfully updated.'.format(book)
            )
            return redirect("book_detail", book.pk)
    else:
        form = BookMediaForm(instance=book)

    return render(
        request,
        "reviews/instance-form.html",
        {"instance": book, "form": form, "model_type": "Book", "is_file_upload": True},
    )
def profile(request):
 return render(request, 'profile.html')
