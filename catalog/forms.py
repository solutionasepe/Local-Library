from typing import Any, Dict
from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from catalog.models import BookInstance
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RenewedBookModelForm(ModelForm):
# class RenewedBookForm(forms.Form):
    # renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_due_back(self):

        data = self.cleaned_data['due_back']

        if data < datetime.date.today():
            raise forms.ValidationError(_("Invalid date - renewal in past"), code="invalid")
            

        
        if data > datetime.date.today() + datetime.timedelta(weeks = 4):
            raise forms.ValidationError(_("Invalid date - renewal more than 4 weeks ahead"), code="invalid")

        return data

    class Meta:
        model = BookInstance
        fields = ["due_back"]
        labels = {'due_back': _('Renewal_date')}
        help_texts = {'due_back': _('Enter a date between now and 4weeks (default 3)')}

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user
      
        
        
    
    
        
    