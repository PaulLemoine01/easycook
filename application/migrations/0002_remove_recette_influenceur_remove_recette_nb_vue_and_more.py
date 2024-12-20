# Generated by Django 4.2.15 on 2024-10-22 08:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recette',
            name='influenceur',
        ),
        migrations.RemoveField(
            model_name='recette',
            name='nb_vue',
        ),
        migrations.RemoveField(
            model_name='recette',
            name='photo',
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('thumbnail', models.ImageField(upload_to='videos')),
                ('nb_vue', models.IntegerField(verbose_name='Nombre de vues')),
                ('nom', models.CharField(max_length=30, verbose_name='Nom')),
                ('description', models.TextField(verbose_name='Description')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('influenceur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.influenceur')),
            ],
        ),
    ]
