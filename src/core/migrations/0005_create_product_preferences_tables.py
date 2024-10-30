
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core', '0004_create_product_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table product_characteristics(
                product_id bigint primary key References vendor_product(product_id) on delete cascade,
                cb_taste_strength char(1) CHECK (cb_taste_strength ~ '[0-9]'), 
                cb_decaf char(1) CHECK (cb_decaf in ('Y', 'N')), 
                cb_flavored char(1) CHECK (cb_flavored in ('Y', 'N')),
                cb_single_origin char(1) CHECK (cb_single_origin in ('Y', 'N')),
                cb_regions varchar(100),
                cb_keywords varchar(100)
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
