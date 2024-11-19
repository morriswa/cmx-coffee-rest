
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0007_create_product_review_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table customer_approved_territory(
                    territory_id varchar(10) primary key,
                    state_code char(2) not null check ( state_code in ('KS','MO','OK') ),
                    country_code char(3) not null check ( country_code in ('USA') ) default 'USA',
                    display_name varchar(32),
                    tax_rate smallint not null default 0
                        check (tax_rate >= 0 and tax_rate <= 100)
                );

                insert into customer_approved_territory
                    (territory_id, state_code, country_code, display_name, tax_rate)
                values
                    ('USA_KS','KS','USA','Kansas, USA', 10),
                    ('USA_MO','MO','USA','Missouri, USA', 5),
                    ('USA_OK','OK','USA','Oklahoma, USA', 2)
                ;

                create table mock_payment(
                    payment_id uuid primary key default gen_random_uuid(),
                    user_id uuid not null references auth_integration(user_id),
                    payment_method char(6) not null default 'dummyd' check (payment_method in ('crcard', 'dbcard', 'extern', 'dummyd')),
                    nickname varchar(32),
                    billing_address_territory varchar(10) not null references customer_approved_territory (territory_id)
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
                drop table if exists customer_approved_territory;
            """
        )
    ]
