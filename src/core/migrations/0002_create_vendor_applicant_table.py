from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0001_create_auth_integration_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table vendor_applicant(
                    application_id bigserial primary key ,
                    user_id uuid not null unique references auth_integration (user_id) on delete cascade ,
                    business_name varchar(256) not null unique ,
                    address_one varchar(256) not null ,
                    address_two varchar(256) ,
                    city varchar(128) not null ,
                    state char(2) not null ,
                    zip char(5) not null ,
                    country char(3) not null ,
                    phone varchar(12) not null ,
                    business_email varchar(256) not null unique ,
                    status char(1) not null default 'N',
                    application_date timestamp not null default current_timestamp
                );
            """,
            reverse_sql="""
                drop table if exists vendor_applicant;
            """
        )
    ]
