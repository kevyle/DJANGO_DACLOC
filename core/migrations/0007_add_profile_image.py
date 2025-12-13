from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_comment_is_active'),
    ]

    # This migration was added and then reverted in code; keep as a no-op to avoid
    # applying a column that no longer exists on the model. Leaving an explicit
    # empty operations list prevents Django from trying to add the removed field.
    operations = []
