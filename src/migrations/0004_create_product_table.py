from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0003_create_vendor_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table vendor_product(
                    product_id bigserial primary key ,
                    vendor_id bigint not null references vendor (vendor_id) on delete cascade ,
                    listed_by uuid not null references auth_integration (user_id) on delete set null ,
                    product_name varchar(64) not null ,
                    description varchar(512) ,
                    initial_price decimal(5,2) not null ,
                    status char(1) not null default 'A' ,
                    date_created timestamp not null default current_timestamp
                );
            """,
            reverse_sql="""
                drop table if exists vendor_product;
            """
        )
    ]
