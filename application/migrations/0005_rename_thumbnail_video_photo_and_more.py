# Generated by Django 4.2.15 on 2024-10-24 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_recette_video'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='thumbnail',
            new_name='photo',
        ),
        migrations.RemoveField(
            model_name='influenceur',
            name='nb_recettes',
        ),
        migrations.AddField(
            model_name='video',
            name='instagram_id',
            field=models.CharField(default='', max_length=30, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='instagram_shortcode',
            field=models.CharField(default='', max_length=30, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='nb_likes',
            field=models.IntegerField(default=0, verbose_name='Nombre de likes'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etape',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='influenceur',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='influenceur',
            name='nb_followers',
            field=models.IntegerField(verbose_name='Followers'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='quantite',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='recette',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='video',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date de création'),
        ),
    ]
