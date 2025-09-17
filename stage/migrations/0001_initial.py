

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("booth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Stage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("image_url", models.URLField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stages",
                        to="booth.location",
                    ),
                ),
            ],
            options={
                "ordering": ["start_time"],
                "indexes": [
                    models.Index(
                        fields=["start_time"], name="stage_stage_start_t_db8156_idx"
                    ),
                    models.Index(
                        fields=["end_time"], name="stage_stage_end_tim_753ab7_idx"
                    ),
                    models.Index(
                        fields=["location"], name="stage_stage_locatio_3f8dd2_idx"
                    ),
                    models.Index(
                        fields=["is_active"], name="stage_stage_is_acti_ea4fea_idx"
                    ),
                    models.Index(fields=["name"], name="stage_stage_name_c657ef_idx"),
                ],
            },
        ),
    ]
