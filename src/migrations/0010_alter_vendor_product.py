from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [('core', '0009_create_newsletter_migration')]
    #Kevin Rivers implemented the newsletter migration on 13 Nov 2024.
    operations = [
        migrations.RunSQL(
            sql = """
                alter table vendor_product
                alter column description type varchar(10000),
                alter column product_name type varchar(128);
            """,
            reverse_sql= """
                alter table vendor_product
                alter column description type varchar(512),
                alter column product_name type varchar(32);
            """
        )
    ]
