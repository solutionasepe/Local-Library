from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Book, BookInstance, Author, Genre, Language
from django.views import generic
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
import requests
from django.contrib.auth import login
from .forms import NewUserForm
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# from catalog.forms import RenewedBookForm
from catalog.forms import RenewedBookModelForm
# Create your views here.

book_id = Book.id

def index(request):
    """View function from homepage of site"""

    # Generate count of some of the main object
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books with status "a"

    num_instances_available = BookInstance.objects.filter(status__exact = 'a').count()

    num_authors = Author.objects.count()

    num_genretype = Genre.objects.count()

    num_book_title = Book.objects.filter(title__icontains = "wild").count()

    num_visits = request.session.get("num_visits", 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genretype": num_genretype,
        "num_book_title": num_book_title,
        "num_visits" : num_visits

    } 

    return render(request, "index.html", context=context)

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return HttpResponseRedirect(reverse("index"))
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form})

class BookListView(generic.ListView):
    model = Book 
    paginate_by = 2


class BookDetailsView(generic.DetailView):
    model = Book
     
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 2

    def get_queryset(self):
        return (BookInstance.objects.filter(borrower=self.request.user).filter(status__exact="o").order_by('due_back'))
    
class Librarians(PermissionRequiredMixin, generic.ListView):

    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_librarians_borrowed.html'
    paginate_by = 2

    def get_queryset(self):    
        return (BookInstance.objects.filter(status__exact='o').order_by('due_back'))

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)    
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewedBookModelForm(request.POST)

        if form.is_valid():
            # form = book_instance.due_back
            
            book_instance.due_back = form.cleaned_data["due_back"]
            book_instance.save()

            # if book_instance.due_back < datetime.date.today():
            #     messages.error(request, "Invalid date - renewal in past")
            #     return HttpResponseRedirect(request.path)

            # elif book_instance.due_back > datetime.date.today() + datetime.timedelta(weeks=4):
            #     messages.error(request, "Invalid date - renewal more than 4 weeks ahead")
            #     return HttpResponseRedirect(reverse('renew-book-librarian', args=[book_instance.id]))
    
            return HttpResponseRedirect(reverse("all-borrowed"))
        
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)

        form = RenewedBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
        # 'error_message': error_message,
    }


    return render(request, 'catalog/book_renew_librarian.html', context)    


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['First_name', "Last_name", "date_of_birth", "date_of_death"]
    initial = {'date_of_death': '11/7/2019'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    permission_required = "catalog.can_mark_returned"

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("books")
    permission_required = 'catalog.can_mark_returned'


@login_required
def borrowed_book(request, pk):
     book_instance = get_object_or_404(BookInstance, pk=pk)
     

     if book_instance.status == 'a':
          book_instance.borrower = request.user
          book_instance.status = 'o'
          book_instance.save()
          return HttpResponseRedirect(reverse("books"))
     else:
        return render(request, "catalog/bookinstance_fail.html", context={"book_instance":book_instance})
     




# def author_detail_view(request, primary_key):
#     try:
#         author = Author.objects.get(pk=primary_key)
#     except Author.DoesNotExist:
#         raise Http404('Author does not exist')

#     return render(request, 'catalog/author_detail_view.html', context={'author': author})



