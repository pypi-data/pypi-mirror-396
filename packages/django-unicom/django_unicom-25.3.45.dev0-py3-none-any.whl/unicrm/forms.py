from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pytz
from django import forms
from django.utils import timezone

from unicom.models import Channel
from unicrm.models import Segment, MailingList, Communication


class CommunicationComposeForm(forms.Form):
    segment = forms.ModelChoiceField(
        queryset=Segment.objects.none(),
        label='Recipient segment',
        help_text='Which contacts should receive this communication.'
    )
    mailing_list = forms.ModelChoiceField(
        queryset=MailingList.objects.none(),
        label='Mailing list',
        required=False,
        help_text='Optional mailing list to target; combined with the segment if both are provided.'
    )
    channel = forms.ModelChoiceField(
        queryset=Channel.objects.none(),
        label='Channel',
        help_text='Channel used to deliver the emails.'
    )
    subject_template = forms.CharField(
        label='Subject',
        max_length=255,
        required=False,
        help_text='Optional Jinja2 subject template. Leave blank to use a generic fallback.'
    )
    content = forms.CharField(
        label='Email content',
        widget=forms.Textarea,
        required=False,
        help_text='Editable HTML body rendered for every contact.'
    )
    follow_up_for = forms.ModelChoiceField(
        queryset=Communication.objects.none(),
        label='Follow-up for',
        required=False,
        help_text='Optional parent communication this one follows up on.',
    )
    skip_antispam_guards = forms.BooleanField(
        label='Skip anti-spam guards',
        required=False,
        help_text='Send even if cooldown/unengaged limits would normally skip a contact.',
    )
    auto_enroll_new_contacts = forms.BooleanField(
        label='Auto-send to new segment members',
        required=False,
        help_text='When checked, any contact who later joins this segment will automatically receive this communication.'
    )
    send_at = forms.CharField(required=False)
    timezone = forms.CharField(required=False)

    def __init__(
        self,
        *args,
        segment_queryset: Iterable[Segment] | None = None,
        mailing_list_queryset: Iterable[MailingList] | None = None,
        channel_queryset: Iterable[Channel] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.fields['segment'].queryset = segment_queryset or Segment.objects.all()
        self.fields['mailing_list'].queryset = mailing_list_queryset or MailingList.objects.all()
        self.fields['channel'].queryset = channel_queryset or Channel.objects.filter(active=True)
        self.fields['follow_up_for'].queryset = Communication.objects.order_by('-created_at')
        self.cleaned_schedule_utc = None
        self.cleaned_schedule_local = None

        if not self.is_bound:
            channel_qs = self.fields['channel'].queryset
            if channel_qs.count() == 1:
                default_channel = channel_qs.first()
                if default_channel:
                    self.initial['channel'] = str(default_channel.pk)
                    self.fields['channel'].initial = str(default_channel.pk)

    def clean_content(self) -> str:
        content = (self.cleaned_data.get('content') or '').strip()
        if not content:
            raise forms.ValidationError('Please provide the email content before sending.')
        return content

    def clean(self):
        cleaned = super().clean()
        follow_up_for = cleaned.get('follow_up_for')
        segment = cleaned.get('segment')
        auto_enroll = cleaned.get('auto_enroll_new_contacts')
        skip_guards = cleaned.get('skip_antispam_guards')

    def clean(self):
        send_at_raw = cleaned.get('send_at')
        timezone_name = (cleaned.get('timezone') or 'UTC').strip() or 'UTC'

        if send_at_raw:
            try:
                naive_dt = datetime.strptime(send_at_raw, '%Y-%m-%dT%H:%M')
            except ValueError:
                self.add_error('send_at', 'Invalid date/time format.')
                return cleaned

            try:
                tz = pytz.timezone(timezone_name)
            except pytz.exceptions.UnknownTimeZoneError:
                tz = pytz.UTC

            local_dt = tz.localize(naive_dt)
            # Store for access after validation
            self.cleaned_schedule_local = local_dt

            utc_dt = local_dt.astimezone(pytz.UTC)
            if utc_dt <= timezone.now():
                self.add_error('send_at', 'Please choose a future time or leave blank to send now.')
            else:
                self.cleaned_schedule_utc = utc_dt
        else:
            self.cleaned_schedule_utc = None
            self.cleaned_schedule_local = None

        if segment and getattr(segment, 'for_followup', False) and not follow_up_for:
            self.add_error('follow_up_for', 'This segment references a previous communication; please choose one.')

        # Follow-ups should be evergreen by default
        if follow_up_for and not auto_enroll:
            cleaned['auto_enroll_new_contacts'] = True

        # Allow skipping guards only for explicit opt-in; no extra validation needed here.
        if skip_guards is None:
            cleaned['skip_antispam_guards'] = False

        return cleaned
