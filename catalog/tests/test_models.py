from django.test import TestCase
from catalog.models import Author

# Create your tests here.

#Example on how to construct a test case class from deriving from testcase.

# class YourTestClass(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         print("SetupTestData: Run ones to setup non-modified data for all class method")
#         pass

#     def setUp(self):
#         print("SetUp: Run once for every test method to setup clean data.")
#         pass

#     def test_false_is_false(self):
#         print("Method: test_false_is_false")
#         self.assertFalse(False)

#     def test_false_is_true(self):
#         print("Method: test_false_is_true")
#         self.assertTrue(True)

#     def test_one_plus_one_equals_two(self):
#         print("Method: test_one_plus_one_equals_two")
#         self.assertEqual(1+1, 2)


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(First_name="Daniel", Last_name="Adewole" )

    def test_First_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('First_name').verbose_name
        self.assertEqual(field_label, 'First name')

    def test_Last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('Last_name').verbose_name
        self.assertEqual(field_label, 'Last name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')
    
    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'date of birth')

    def test_first_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('First_name').max_length
        self.assertEqual(max_length, 100)

    def test_Last_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('Last_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_Last_name_comma_First_name(self):
        author = Author.objects.get(id =1 )
        expected_object_name = "{0}, {1}".format(author.Last_name, author.First_name)
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), '/catalog/authors/1')
    