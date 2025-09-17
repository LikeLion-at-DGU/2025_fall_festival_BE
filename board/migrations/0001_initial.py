import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Board",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="Lost",
            fields=[
                (
                    "board_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="board.board",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("location", models.CharField(max_length=200)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("board.board",),
        ),
        migrations.CreateModel(
            name="Notice",
            fields=[
                (
                    "board_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="board.board",
                    ),
                ),
                ("is_emergency", models.BooleanField(default=False)),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("board.board",),
        ),
    ]