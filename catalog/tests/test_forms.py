import datetime

from django.test import TestCase
from catalog.forms import RenewedBookModelForm
from catalog.models import BookInstance, Book
import uuid

from django.utils import timezone

class RenewedBookModelFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        book = Book.objects.create(title="Test book")
        BookInstance.objects.create(book=book, id=uuid.uuid4())

    def test_renew_form_date_label(self):
        form = RenewedBookModelForm()
        self.assertTrue(form.fields["due_back"].label is None or form.fields['due_back'].label == 'Renewal_date')

    def test_renew_form_date_help_text(self):
        form = RenewedBookModelForm()
        field_help_text = form.fields['due_back'].help_text
        self.assertEqual(field_help_text, "Enter a date between now and 4weeks (default 3)")

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewedBookModelForm(data={"due_back": date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewedBookModelForm(data= {'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewedBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewedBookModelForm(data={"due_back": date})
        self.assertTrue(form.is_valid())