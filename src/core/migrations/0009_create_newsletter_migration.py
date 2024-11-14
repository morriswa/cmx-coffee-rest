from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [('core', '0008_create_mock_payment_and_order_table')]
    #Kevin Rivers implemented the newsletter migration on 13 Nov 2024.
    operations = [
        migrations.RunSQL(
            sql = """
                alter table customer_preferences
                add column newsletter char(1)
                    not null default 'n'
                    check ( newsletter in ('y', 'n') );
            """,
            reverse_sql= """
                alter table customer_preferences
                drop column newsletter;
            """
        )
    ]
