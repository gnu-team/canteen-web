from django import forms
from django.contrib.auth.models import User
from canteen.models import Profile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self):
        user = super().save()

        # Make a profile for this user
        profile = Profile.objects.create(user=user)
        # For now, make everyone who registers a User
        # XXX Don't hardcode this
        profile.set_group('Users')
        profile.save()

        return user
