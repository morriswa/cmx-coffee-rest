from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0002_create_vendor_applicant_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table vendor(
                    vendor_id bigserial primary key ,
                    user_id uuid not null unique references auth_integration (user_id) ,
                    business_name varchar(256) not null unique ,
                    business_email varchar(256) not null unique ,
                    phone varchar(12) not null ,
                    address_one varchar(256) not null ,
                    address_two varchar(256) ,
                    city varchar(128) not null ,
                    zip char(5) not null ,
                    territory bigint not null references vendor_approved_territory(territory_id),
                    status char(1) not null default 'A',
                    approved_by uuid references auth_integration (user_id) ,
                    creation_date timestamp not null default current_timestamp
                );
            """,
            reverse_sql="""
                drop table if exists vendor;
            """
        )
    ]
