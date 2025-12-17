from django import forms
from django.conf import settings

from .conf import booking_settings
from .utils import prepare_addon_choices


class BookingDetailsForm(forms.Form):
    client_name = forms.CharField(label="Your name", max_length=255)
    email = forms.EmailField(label="Email", required=False)
    phone = forms.CharField(label="Phone", required=False, max_length=50)
    notes = forms.CharField(label="Notes", required=False, widget=forms.Textarea)

    def __init__(self, *args, addon_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if addon_choices:
            self.fields["addons"] = forms.MultipleChoiceField(
                label="Add-ons",
                required=False,
                widget=forms.CheckboxSelectMultiple,
                choices=prepare_addon_choices(addon_choices),
            )


class PortalLookupForm(forms.Form):
    reference = forms.CharField(label="Booking reference", max_length=100)
    email = forms.EmailField(label="Email")


class RescheduleForm(forms.Form):
    slot = forms.CharField(widget=forms.HiddenInput)
    provider = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_slot(self):
        value = self.cleaned_data["slot"]
        if not value:
            raise forms.ValidationError("A new slot must be selected.")
        return value
