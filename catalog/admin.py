from django.contrib import admin
from .models import Author, Book, BookInstance, Genre, Language
# Register your models here.

# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language) 

class BookInline(admin.TabularInline):
    model = Book

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("First_name", "Last_name", "date_of_birth", "date_of_death") 
    fields = ["First_name", "Last_name", ("date_of_birth", "date_of_death")]

    inlines = [BookInline]

admin.site.register(Author, AuthorAdmin)

class BookInstanceInline(admin.TabularInline):
    
    model = BookInstance


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "language", "display_genre")

    inlines = [BookInstanceInline]
    

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ("book", "status", "due_back", "id", "borrower")
    list_filter = ("status", "due_back")
    fieldsets = (
        (
        None, {
        "fields": ("book", "imprint", "id")
        }
        ),
        ("Availiabiltiy", 
         {"fields": ("status", "due_back", "borrower")})
    )


