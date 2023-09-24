# Generated by Django 4.1.7 on 2023-04-08 06:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_book_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='language',
            field=models.ForeignKey(max_length=200, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.language'),
        ),
    ]
