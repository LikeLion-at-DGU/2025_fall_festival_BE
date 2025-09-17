import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("board", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BoothCoupon",
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
                ("price", models.IntegerField()),
                ("is_used", models.BooleanField(default=False)),
                ("serial_number", models.CharField(max_length=50)),
            ],
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
                    "coupon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event.boothcoupon",
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
