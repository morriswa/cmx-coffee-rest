from django.db import migrations


class Migration(migrations.Migration):

    dependencies = []
    operations = [
        migrations.RunSQL(
            sql="""
                create table auth_integration(
                    user_id uuid primary key default gen_random_uuid(),
                    email varchar(256) not null unique
                );
            """,
            reverse_sql="""
                drop table if exists auth_integration;
            """
        )
    ]
