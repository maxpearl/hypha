from django import forms
from django.db.models import Q

from addressfield.fields import AddressField
from opentech.apply.funds.models import ApplicationSubmission
from opentech.apply.stream_forms.fields import MultiFileField
from opentech.apply.users.groups import STAFF_GROUP_NAME

from .models import (
    COMMITTED,
    Approval,
    Contract,
    PacketFile,
    PaymentReceipt,
    PaymentRequest,
    Project
)


class ApproveContractForm(forms.ModelForm):
    name = 'approve_contract_form'

    class Meta:
        fields = ['id']
        model = Contract
        widgets = {'id': forms.HiddenInput()}

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.instance.is_signed:
            raise forms.ValidationError('You can only approve a signed contract')

        super().clean()


class CreateProjectForm(forms.Form):
    submission = forms.ModelChoiceField(
        queryset=ApplicationSubmission.objects.filter(project__isnull=True),
        widget=forms.HiddenInput(),
    )

    def __init__(self, instance=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if instance:
            self.fields['submission'].initial = instance.id

    def save(self, *args, **kwargs):
        submission = self.cleaned_data['submission']
        return Project.create_from_submission(submission)


class CreateApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = ['by']
        widgets = {'by': forms.HiddenInput()}

    def __init__(self, user=None, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        initial.update(by=user)
        super().__init__(*args, initial=initial, **kwargs)


class ProjectEditForm(forms.ModelForm):
    contact_address = AddressField()

    class Meta:
        fields = [
            'title',
            'contact_legal_name',
            'contact_email',
            'contact_address',
            'contact_phone',
            'value',
            'proposed_start',
            'proposed_end',
        ]
        model = Project
        widgets = {
            'title': forms.TextInput,
            'contact_legal_name': forms.TextInput,
            'contact_email': forms.TextInput,
            'contact_phone': forms.TextInput,
            'proposed_end': forms.DateInput,
            'proposed_start': forms.DateInput,
        }


class ProjectApprovalForm(ProjectEditForm):
    def save(self, *args, **kwargs):
        self.instance.user_has_updated_details = True
        return super().save(*args, **kwargs)


class RejectionForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)

    def __init__(self, instance=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RemoveDocumentForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        fields = ['id']
        model = PacketFile

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RequestPaymentForm(forms.ModelForm):
    receipts = MultiFileField()

    class Meta:
        fields = ['value', 'invoice', 'date_from', 'date_to', 'receipts', 'comment']
        model = PaymentRequest
        widgets = {
            'date_from': forms.DateInput,
            'date_to': forms.DateInput,
        }

    def __init__(self, user=None, instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data['date_from']
        date_to = cleaned_data['date_to']

        if date_from > date_to:
            self.add_error('date_from', 'Date From must be before Date To')

        return cleaned_data

    def save(self, commit=True):
        request = super().save(commit=commit)

        PaymentReceipt.objects.bulk_create(
            PaymentReceipt(payment_request=request, file=receipt)
            for receipt in self.cleaned_data['receipts']
        )

        return request


class SetPendingForm(forms.ModelForm):
    class Meta:
        fields = ['id']
        model = Project
        widgets = {'id': forms.HiddenInput()}

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.instance.status != COMMITTED:
            raise forms.ValidationError('A Project can only be sent for Approval when Committed.')

        if self.instance.is_locked:
            raise forms.ValidationError('A Project can only be sent for Approval once')

        super().clean()

    def save(self, *args, **kwargs):
        self.instance.is_locked = True
        return super().save(*args, **kwargs)


class UploadContractForm(forms.ModelForm):
    class Meta:
        fields = ['file', 'is_signed']
        model = Contract

    def __init__(self, user=None, instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not user.is_staff:
            self.fields['is_signed'].widget = forms.HiddenInput()
            self.fields['is_signed'].default = True


class UploadDocumentForm(forms.ModelForm):
    class Meta:
        fields = ['title', 'category', 'document']
        model = PacketFile
        widgets = {'title': forms.TextInput()}

    def __init__(self, user=None, instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdateProjectLeadForm(forms.ModelForm):
    class Meta:
        fields = ['lead']
        model = Project

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lead_field = self.fields['lead']
        lead_field.label = f'Update lead from {self.instance.lead} to'

        qwargs = Q(groups__name=STAFF_GROUP_NAME) | Q(is_superuser=True)
        lead_field.queryset = (lead_field.queryset.exclude(pk=self.instance.lead_id)
                                                  .filter(qwargs)
                                                  .distinct())