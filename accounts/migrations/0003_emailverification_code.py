# Generated manually after switching registration verification to OTP.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_emailloginotp'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverification',
            name='code',
            field=models.CharField(blank=True, max_length=6),
        ),
    ]
