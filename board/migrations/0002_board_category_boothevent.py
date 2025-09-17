

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0001_initial"),
        ("booth", "0002_booth_operate_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="category",
            field=models.CharField(
                choices=[
                    ("Notice", "공지"),
                    ("LostItem", "분실물"),
                    ("Event", "이벤트"),
                ],
                default="Notice",
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name="BoothEvent",
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
                ("title", models.CharField(max_length=50)),
                ("detail", models.TextField()),
                ("start_time", models.DateField()),
                ("end_time", models.DateField()),
                (
                    "booth",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="booth.booth"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("board.board",),
        ),
    ]
