from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bots", "0078_sharedrecordinglink_sharedrecordingaccess"),
    ]

    operations = [
        migrations.AddField(
            model_name="sharedrecordinglink",
            name="title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
