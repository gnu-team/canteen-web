from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import validate_password
from canteen.models import Profile

class RegisterForm(forms.Form):
    username = forms.CharField(validators=(UnicodeUsernameValidator,))
    password = forms.CharField(widget=forms.PasswordInput, validators=(validate_password,))

    def save(self):
        user = User.objects.create_user(username=self.cleaned_data['username'],
                                        password=self.cleaned_data['password'])
        # Make a profile for this user
        profile = Profile.objects.create(user=user)
        # For now, make everyone who registers a User
        # XXX Don't hardcode this
        profile.set_group('Users')
        profile.save()

        return user
