# Generated by Django 3.2.12 on 2023-04-03 19:10

from django.db import migrations, models
import sorl.thumbnail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_auto_20230328_1718"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userimage",
            name="image",
            field=models.ImageField(upload_to=""),
        ),
        migrations.AlterField(
            model_name="userimage",
            name="thumbnail_200",
            field=sorl.thumbnail.fields.ImageField(upload_to=""),
        ),
        migrations.AlterField(
            model_name="userimage",
            name="thumbnail_400",
            field=sorl.thumbnail.fields.ImageField(upload_to=""),
        ),
    ]
