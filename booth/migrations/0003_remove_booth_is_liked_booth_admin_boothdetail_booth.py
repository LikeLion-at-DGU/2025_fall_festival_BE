

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("adminuser", "0001_initial"),
        ("booth", "0002_booth_operate_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="booth",
            name="is_liked",
        ),
        migrations.AddField(
            model_name="booth",
            name="admin",
            field=models.ForeignKey(
<<<<<<< HEAD
                default=1,
=======
                blank=True,
                null=True,
>>>>>>> 5da09ca7b89b638d488ac262bf5e4923a4e7d16d
                on_delete=django.db.models.deletion.CASCADE,
                to="adminuser.admin",
            ),
        ),
        migrations.AddField(
            model_name="boothdetail",
            name="booth",
            field=models.OneToOneField(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="booth.booth"
            ),
            preserve_default=False,
        ),
    ]
