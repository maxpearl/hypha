# Generated by Django 2.0.2 on 2018-07-19 14:20

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0005_streamform'),
        ('funds', '0035_author_timestamp_revision'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundReviewForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='review.ReviewForm')),
                ('fund', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_forms', to='funds.FundType')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LabReviewForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='review.ReviewForm')),
                ('lab', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_forms', to='funds.LabType')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]