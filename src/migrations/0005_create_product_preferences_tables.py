
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core', '0004_create_product_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                -- author: Timothy Holmes
                create table product_characteristics(
                    product_id bigint primary key references vendor_product(product_id) on delete cascade,
                    cb_taste_strength char(1) check (cb_taste_strength ~ '[0-9]'),
                    cb_decaf char(1) check (cb_decaf in ('y', 'n')),
                    cb_flavored char(1) check (cb_flavored in ('y', 'n')),
                    cb_single_origin char(1) check (cb_single_origin in ('y', 'n')),
                    cb_regions varchar(100),
                    cb_keywords varchar(1000)
                );

                -- author: Rahul Bhattachan
                create table customer_preferences(
                    user_id UUID PRIMARY KEY REFERENCES auth_integration (user_id) ON DELETE CASCADE,
                    p_cb_strength_mild CHAR(1) CHECK (p_cb_strength_mild IN ('y', 'n')),
                    p_cb_strength_med CHAR(1) CHECK (p_cb_strength_med IN ('y', 'n')),
                    p_cb_strength_bold CHAR(1) CHECK (p_cb_strength_bold IN ('y', 'n')),
                    p_cb_strength_blonde CHAR(1) CHECK (p_cb_strength_blonde IN ('y', 'n')),
                    p_cb_caf CHAR(1) CHECK (p_cb_caf IN ('y', 'n')),
                    p_cb_decaf CHAR(1) CHECK (p_cb_decaf IN ('y', 'n')),
                    p_cb_flavored CHAR(1) CHECK (p_cb_flavored IN ('y', 'n')),
                    p_cb_origin_single CHAR(1) CHECK (p_cb_origin_single IN ('y', 'n')),
                    p_cb_origin_blend CHAR(1) CHECK (p_cb_origin_blend IN ('y', 'n')),
                    p_cb_keywords VARCHAR(1000)
                );
            """,
            reverse_sql="""
                drop table if exists product_characteristics;
                drop table if exists customer_preferences;
            """
        )
    ]
