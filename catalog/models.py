from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import date
import uuid 

# Create your models here.
class Genre(models.Model):
    """Model representing the book Genre"""

    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g Science or Fiction)")

    def __str__(self):
        return self.name
    
# class GenreManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().annotate(genre_type = models.functions.Lower("name"))

# class Genre(models.Model):
#     name =  models.CharField(max_length=200, help_text="Enter a book genre (e.g Science or Fiction)")
#     objects = GenreManager()

class Language(models.Model):
    name = models.CharField(max_length=200, help_text="Enter the language used in writing this book")

    def __str__(self):
        return self.name  


class Book(models.Model):

    title = models.CharField(max_length=200)

    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text="Enter a description of the book")

    isbn = models.CharField('ISBN', max_length = 13, unique=True, 
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    
    genre = models.ManyToManyField(Genre, help_text="Select a Genre for this book")

    language = models.ForeignKey('Language', max_length=200, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse ('book-details', args=[str(self.id)])
    
    def display_genre(self):
        return ", ".join(genre.name for genre in self.genre.all()[:3])
    
    display_genre.short_description = "Genre"

class BookInstance(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, 
                          help_text="Unique id to for this particular book across the library")
    book = models.ForeignKey("Book", on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(to=get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reversed")
    )

    status = models.CharField(
        max_length = 1,
        choices = LOAN_STATUS,
        blank = True,
        default= "m",
        help_text= "Book Availability"
        )

    class meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return "{0} ({1})".format(self.id, self.book.title)
    
    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)
    
class Author(models.Model):
    First_name = models.CharField(max_length=100)
    Last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null= True, blank=True)
    date_of_death = models.DateField("died", null=True, blank=True)

    class Meta:
        ordering = ['First_name', 'Last_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])
    
    def __str__(self):

        return "{0}, {1}".format(self.Last_name, self.First_name)
    
        
    

