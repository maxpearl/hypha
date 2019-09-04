# Generated by Django 2.0.13 on 2019-08-27 08:25

from django.db import migrations

from opentech.apply.activity.models import ACTION, TEAM, ALL


def update_visibility_options(apps, schema_editor):
    Activity = apps.get_model('activity', 'Activity')
    for activity in Activity.objects.filter(type=ACTION):
        updated = False
        if activity.visibility == 'public':
            activity.visibility = ALL
            updated = True
        elif activity.visibility == 'internal':
            activity.visibility = TEAM
            updated = True

        if updated:
            activity.save()


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0026_update_visibility_options'),
    ]

    operations = [
        migrations.RunPython(update_visibility_options, migrations.RunPython.noop)
    ]