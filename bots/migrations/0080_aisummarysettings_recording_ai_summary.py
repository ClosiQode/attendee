# Generated migration for AI Summary Settings and Recording AI Summary fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0079_sharedrecordinglink_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='AISummarySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False)),
                ('provider', models.IntegerField(choices=[(1, 'OpenAI'), (2, 'Anthropic'), (3, 'Mistral')], default=1)),
                ('system_prompt', models.TextField(default='Tu es un assistant spécialisé dans la synthèse de réunions professionnelles. À partir de la transcription fournie, génère une synthèse structurée comprenant :\n\n## Résumé\nUn résumé concis de la réunion en 2-3 phrases.\n\n## Points clés\nLes points importants abordés durant la réunion.\n\n## Décisions prises\nLes décisions qui ont été prises.\n\n## Actions à faire\nLes actions à entreprendre, avec les responsables si mentionnés.')),
                ('model_name', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_summary_settings', to='bots.project')),
            ],
        ),
        migrations.AddField(
            model_name='recording',
            name='ai_summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='ai_summary_status',
            field=models.IntegerField(choices=[(0, 'Not Started'), (1, 'In Progress'), (2, 'Complete'), (3, 'Failed')], default=0),
        ),
        migrations.AddField(
            model_name='recording',
            name='ai_summary_failure_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
