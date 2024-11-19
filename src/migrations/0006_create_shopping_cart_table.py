
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0005_create_product_preferences_tables')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table shopping_cart(
                    id bigserial primary key,
                    user_id uuid not null references auth_integration (user_id) on delete cascade,
                    product_id bigint not null references vendor_product (product_id) on delete cascade,
                    quantity smallint not null default 0
                );
            """,
            reverse_sql="""
                drop table if exists shopping_cart;
            """
        )
    ]
