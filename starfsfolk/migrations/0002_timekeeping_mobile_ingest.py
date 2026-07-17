from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starfsfolk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timaklukkuatburdur',
            name='client_event_id',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True, verbose_name='Client event ID'),
        ),
        migrations.AddField(
            model_name='timaklukkuatburdur',
            name='raw_payload',
            field=models.JSONField(blank=True, default=dict, verbose_name='Raw payload'),
        ),
        migrations.AlterField(
            model_name='timaklukkuatburdur',
            name='source',
            field=models.CharField(choices=[('PHONE', 'Phone'), ('MOBILE', 'Mobile'), ('BIXBY', 'Bixby'), ('ADMIN', 'Admin'), ('SYSTEM', 'System'), ('API', 'API')], default='API', max_length=20, verbose_name='Uppruni'),
        ),
    ]
