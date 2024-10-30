
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core', '0004_create_product_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table product_characteristics(

                );

                create table customer_preferences(

                );
            """,
            reverse_sql="""
                drop table if exists product_characteristics;
                drop table if exists customer_preferences;
            """
        )
    ]
