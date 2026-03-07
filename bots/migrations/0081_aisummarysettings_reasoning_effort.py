# Generated migration for reasoning_effort field in AISummarySettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0080_aisummarysettings_recording_ai_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='aisummarysettings',
            name='reasoning_effort',
            field=models.CharField(blank=True, default='low', max_length=10),
        ),
    ]
