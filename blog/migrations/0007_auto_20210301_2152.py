# Generated by Django 3.1.7 on 2021-03-01 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20210301_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='belong_lanmu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article_lanmu', to='blog.lanmu'),
        ),
        migrations.AlterField(
            model_name='lanmu',
            name='belong',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lanmu_child', to='blog.lanmu'),
        ),
    ]
