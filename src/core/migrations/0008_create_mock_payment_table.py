
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0007_create_product_review_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table mock_payment(
                    payment_id uuid primary key default gen_random_uuid(),
                    user_id uuid not null references auth_integration(user_id) on delete cascade,
                    payment_method char(6) not null default 'dummyd' check (payment_method in ('crcard', 'dbcard', 'extern', 'dummyd')),
                    nickname varchar(32)
                );
            """,
            reverse_sql="""
                drop table if exists mock_payment;
            """
        )
    ]
