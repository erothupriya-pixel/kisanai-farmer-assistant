from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, help_text='City or village name', max_length=200)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('primary_crops', models.CharField(blank=True, help_text='Comma-separated list of crops', max_length=500)),
                ('land_area', models.FloatField(blank=True, help_text='Land area in acres', null=True)),
                ('preferred_language', models.CharField(choices=[('en', 'English'), ('hi', 'Hindi'), ('te', 'Telugu')], default='en', max_length=5)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='farmer_profile', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('language', models.CharField(default='en', max_length=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions', to='auth.user')),
            ],
            options={'ordering': ['-updated_at']},
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], max_length=10)),
                ('content', models.TextField()),
                ('input_type', models.CharField(choices=[('text', 'Text'), ('voice', 'Voice')], default='text', max_length=10)),
                ('language', models.CharField(default='en', max_length=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='app.chatsession')),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='DailyFarmingTip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('language', models.CharField(choices=[('en', 'English'), ('hi', 'Hindi'), ('te', 'Telugu')], default='en', max_length=5)),
                ('season', models.CharField(choices=[('kharif', 'Kharif (Jun-Sep)'), ('rabi', 'Rabi (Oct-Mar)'), ('zaid', 'Zaid (Mar-Jun)'), ('all', 'All Seasons')], default='all', max_length=10)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='WeatherCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=200)),
                ('data', models.JSONField()),
                ('fetched_at', models.DateTimeField(auto_now=True)),
            ],
            options={'unique_together': {('location',)}},
        ),
    ]
