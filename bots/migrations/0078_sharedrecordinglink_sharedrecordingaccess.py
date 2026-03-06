# Generated migration for SharedRecordingLink and SharedRecordingAccess

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0077_alter_participantevent_event_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedRecordingLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(editable=False, max_length=32, unique=True)),
                ('token', models.CharField(editable=False, max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('access_count', models.IntegerField(default=0)),
                ('allow_download', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_links', to='bots.recording')),
            ],
        ),
        migrations.CreateModel(
            name='SharedRecordingAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accessed_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('shared_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accesses', to='bots.sharedrecordinglink')),
            ],
            options={
                'ordering': ['-accessed_at'],
            },
        ),
    ]
