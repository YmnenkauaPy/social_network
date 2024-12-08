from django import forms
from authentication import models

# class ProfileForm(forms.ModelForm):
#     username = forms.CharField(max_length=30, required=True)

#     class Meta:
#         model = models.CustomUser
#         fields = ['username', 'details', 'profile_picture']
#         widgets = {
#             'profile_picture': forms.FileInput(),
#         }