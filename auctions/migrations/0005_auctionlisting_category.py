# Generated by Django 4.1 on 2023-04-24 18:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0004_remove_auctionlisting_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="auctionlisting",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="category",
                to="auctions.category",
            ),
        ),
    ]