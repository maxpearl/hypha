# Generated by Django 2.0.13 on 2019-07-10 17:33

from django.db import migrations
from django.db.models import F


def submission_to_source(apps, schema_editor):
    Activity = apps.get_model('activity', 'Activity')
    if Activity.objects.exists():
        ContentType = apps.get_model('contenttypes', 'ContentType')
        content_type = ContentType.objects.get(model='applicationsubmission', app_label='funds')
        Activity.objects.update(
            source_object_id=F('submission_id'),
            source_content_type=content_type,
        )


def source_to_submission(apps, schema_editor):
    Activity = apps.get_model('activity', 'Activity')
    Activity.objects.update(submission_id=F('source_object_id'))


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0028_add_new_generic_relation'),
        ('funds', '0065_applicationsubmission_meta_categories'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(submission_to_source, source_to_submission)
    ]