from django.test import TestCase
from catalog.models import Author, Book, BookInstance, Language, Genre
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import uuid
import datetime
# import uuid
# from django.contrib.auth.models import Permission

from django.urls import reverse

class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        number_of_author = 13
        for author_id in range(number_of_author):
            Author.objects.create(
                First_name = "Dominique {}".format(author_id),
                Last_name = "surname {}".format(author_id)
            )

    def test_url_exist_at_the_required_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_assersible_by_name(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_list.html")

    def test_pagination_is_two(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context['author_list']), 2)

    def test_list_all_authors(self):
        response = self.client.get(reverse("authors") + "?page = 2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context['author_list']), 2)


class LoanBookInstanceByUserTest(TestCase):

    
    def setUp(self):

        test_user1 = User.objects.create_user(username ="Asepe", password="anyone")
        test_user2 = User.objects.create_user(username="Taiwo", password = "come")

        test_user1.save()
        test_user2.save()

        #create a book
        test_author = Author.objects.create(First_name ="John", Last_name="Smith")
        test_genre = Genre.objects.create(name = "Fantasy")
        test_language = Language.objects.create(name = "English")
        test_book = Book.objects.create(
            title = "Book title",
            summary = "This is a book",
            isbn = "ABCD",
            language = test_language,
            author = test_author

        )

        #create a genre as a post-setup
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)

        test_book.save()


        #creating book instance
        number_of_copies_of_books = 30

        for book_copy in range(number_of_copies_of_books):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = "m"
            BookInstance.objects.create(
                book = test_book,
                imprint = "Unlikely 2020",
                due_back = return_date,
                status = status,
                borrower = the_borrower
            )
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("my-borrowed"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/mybooks/")

    def test_login_use_correct_template(self):
        login = self.client.login(username="Asepe", password="anyone")
        response = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(response.context["user"]), "Asepe")
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "catalog/bookinstance_list_borrowed_user.html")

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username="Asepe", password="anyone")
        response = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(response.context["user"]), "Asepe")
        
        self.assertEqual(response.status_code, 200)

        self.assertTrue("bookinstance_list" in response.context)
        self.assertEqual(len(response.context["bookinstance_list"]), 0)

        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        response = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(response.context["user"]), "Asepe")
        self.assertEqual(response.status_code, 200)

        self.assertTrue("bookinstance_list" in response.context)

        for bookinstance in response.context["bookinstance_list"]:
            self.assertEqual(response.context["user"], bookinstance.borrower)
            self.assertEqual(bookinstance.status, 'o')

    def test_pages_ordered_by_due_date(self):

        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username="Asepe", password="anyone")
        response = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(response.context['user']), "Asepe")
        self.assertEqual(response.status_code, 200)

        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context['bookinstance_list']), 2)

        last_date = 0

        for book in response.context["bookinstance_list"]:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back

class RenewedBookInstanceTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username="Asepe", password="anyone")
        test_user2 = User.objects.create_user(username="Solution", password="password123DKJ")

        test_user1.save()
        test_user2.save()

        permission, created = Permission.objects.get_or_create(
                                            codename="can_mark_returned", 
                                            name="Set book as returned", 
                                            content_type= ContentType.objects.get_for_model(BookInstance),
                                            )
        test_user2.user_permissions.add(permission)
        test_user2.save()
        # permission = Permission.objects.get(name="Set as returned")
        # test_user2.user_permissions.add(permission)
        # test_user2.save()

        
        test_author = Author.objects.create(First_name="John", Last_name="smith")
        test_language = Language.objects.create(name="English")
        test_genre = Genre.objects.create(name="Fantasy")

        test_book = Book.objects.create(
            title = "Book title",
            author = test_author,
            language = test_language,
            summary = "This is a book",
            isbn = "ABCD"
        )

        genre_objects_for_books = Genre.objects.all()
        test_book.genre.set(genre_objects_for_books)
        test_book.save()

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            id = uuid.uuid4(),
            book = test_book,
            imprint = "Unlikley since 2020",
            due_back = return_date,
            borrower = test_user1,
            status = 'o'
        )

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            id = uuid.uuid4(),
            book = test_book,
            imprint = " Unlikley since 2020",
            due_back = return_date,
            borrower = test_user2,
            status = "o",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={"pk": self.test_bookinstance1.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='Asepe', password='anyone')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='Solution', password='password123DKJ')
        response = self.client.get(reverse('renew-book-librarian', kwargs={"pk": self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_books(self):
        login = self.client.login(username="Solution", password='password123DKJ')
        response = self.client.get(reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk}))

        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        login = self.client.login(username="Solution", password="password123DKJ")
        response = self.client.get(reverse("renew-book-librarian", kwargs={'pk':test_uid}))
        self.assertEqual(response.status_code, 404)
        
    def test_correct_template_used(self):
        login = self.client.login(username='Solution', password="password123DKJ")
        response = self.client.get(reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_intitial_date_is_four_weeks_in_the_future(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        response = self.client.get(reverse("renew-book-librarian", kwargs={"pk":self.test_bookinstance2.pk}))

        self.assertEqual(response.status_code, 200)
        date_3_weeks_in_the_future = datetime.date.today() + datetime.timedelta(weeks=3)

        self.assertEqual(response.context['form'].initial['due_back'], date_3_weeks_in_the_future)

    def test_redirect_to_all_borrowed_book_list_on_sucess(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        valid_date_in_the_future = datetime.date.today() + datetime.timedelta(weeks=2)

        response = self.client.post(reverse('renew-book-librarian', kwargs={"pk": self.test_bookinstance2.pk, }), {"due_back":valid_date_in_the_future})
        self.assertRedirects(response, reverse("all-borrowed"))

    def test_form_invalid_renewal_date_in_past(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)

        response = self.client.post(reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance2.pk}), {"due_back":date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "due_back", "Invalid date - renewal in past")
        # self.assertRedirects(response, response.context['request'].path)

    def test_form_invalid_renewal_date_in_future(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)

        response = self.client.post(reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance2.pk}), {"due_back": date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', "Invalid date - renewal more than 4 weeks ahead")

    
class AuthorCreateTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(username="Asepe", password="anyone")
        test_user2 = User.objects.create_user(username="Solution", password="password123DKJ")
        test_user1.save()
        test_user2.save()

        permission, create = Permission.objects.get_or_create(
            codename = "can_mark_returned",
            name = "Set book as returned",
            content_type = ContentType.objects.get_for_model(BookInstance)
        )
        test_user2.user_permissions.add(permission, create)
        test_user2.save()

        author = Author.objects.create(First_name="Jack", Last_name="smith")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("author-create"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/author/create/")

    def test_forbidden_if_logged_in_but_without_permission(self):
        login = self.client.login(username='Asepe', password="anyone")
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response.status_code, 403)

    def test_log_in_with_correct_permission(self):
        login = self.client.login(username='Solution', password="password123DKJ")
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_log_in_with_correct_template(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_form.html")

    def test_form_intial_as_date_of_death(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        response = self.client.get(reverse("author-create"))

        self.assertEqual(response.status_code, 200)
        date_of_death = datetime.date(2019, 7, 11)

        response_date = response.context["form"].initial["date_of_death"]
        date_object = datetime.datetime.strptime(response_date, '%d/%m/%Y').date()

        self.assertEqual(date_object, date_of_death)

    def test_redirect_to_detail_on_sucess(self):
        login = self.client.login(username="Solution", password="password123DKJ")
        response = self.client.post(
            reverse("author-create"),
            {
                "First_name": "Jack",
                "Last_name": "Smith",
            }
         )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/catalog/authors/"))


