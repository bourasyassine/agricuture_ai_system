from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Count


def backfill_anomaly_events(apps, schema_editor):
    AnomalyEvent = apps.get_model("core", "AnomalyEvent")
    db_alias = schema_editor.connection.alias

    # Ensure plot/message/recommendation are populated for existing records.
    for event in AnomalyEvent.objects.using(db_alias).select_related("reading__plot"):
        changed = False

        if getattr(event, "plot_id", None) is None and getattr(event, "reading_id", None):
            event.plot_id = event.reading.plot_id
            changed = True

        if not getattr(event, "message", None):
            event.message = ""
            changed = True

        if not getattr(event, "recommendation", None):
            event.recommendation = ""
            changed = True

        if changed:
            event.save(using=db_alias)

    # Deduplicate so the unique constraint on reading can be applied safely.
    duplicates = (
        AnomalyEvent.objects.using(db_alias)
        .values("reading_id")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )

    for duplicate in duplicates:
        events = (
            AnomalyEvent.objects.using(db_alias)
            .filter(reading_id=duplicate["reading_id"])
            .order_by("-created_at", "-id")
        )
        keeper = events.first()
        for extra in events[1:]:
            extra.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_farmprofile_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='anomalyevent',
            old_name='detected_at',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='anomalyevent',
            name='message',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='anomalyevent',
            name='plot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='anomaly_events', to='core.fieldplot'),
        ),
        migrations.AddField(
            model_name='anomalyevent',
            name='recommendation',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='agentrecommendation',
            name='anomaly',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='agent_recommendation', to='core.anomalyevent'),
        ),
        migrations.AlterModelOptions(
            name='anomalyevent',
            options={'ordering': ['-created_at']},
        ),
        migrations.RunPython(backfill_anomaly_events, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='anomalyevent',
            constraint=models.UniqueConstraint(fields=('reading',), name='unique_anomaly_per_reading'),
        ),
    ]
