
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0007_create_product_review_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table mock_payment(
                    payment_id uuid primary key default gen_random_uuid(),
                    user_id uuid not null references auth_integration(user_id),
                    payment_method char(6) not null default 'dummyd' check (payment_method in ('crcard', 'dbcard', 'extern', 'dummyd')),
                    nickname varchar(32)
                );

                create table mock_order(
                    order_id uuid primary key default gen_random_uuid(),
                    user_id uuid not null references auth_integration(user_id),
                    payment_id uuid references mock_payment (payment_id),
                    payment_status char(4) not null check (payment_status in ('paid', 'none', 'decl')) default 'none',
                    status char(7) not null check (status in ('shipped', 'process', 'incompl')) default 'incompl',
                    subtotal decimal(5,2) not null,
                    tax_rate smallint not null
                        check (0 <= tax_rate and tax_rate <= 100)
                        default 0,
                    tax decimal(5,2) not null,
                    total decimal(5,2) not null
                );

                create table mock_order_item(
                    order_item_id bigserial primary key,
                    order_id uuid not null references mock_order (order_id),
                    product_id bigint not null references vendor_product (product_id),
                    quantity smallint not null,
                    each_price decimal(5,2) not null
                );
            """,
            reverse_sql="""
                drop table if exists mock_order_item;
                drop table if exists mock_order;
                drop table if exists mock_payment;
            """
        )
    ]
