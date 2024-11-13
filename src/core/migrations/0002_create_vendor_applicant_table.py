from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('core', '0001_create_auth_integration_table')]

    operations = [
        migrations.RunSQL(
            sql="""
                create table vendor_approved_territory(
                    territory_id varchar(10) primary key ,
                    state_code char(2) not null unique ,
                    country_code char(3) not null ,
                    display_name varchar(32) not null unique
                );

                insert into vendor_approved_territory(territory_id, state_code, country_code, display_name)
                values
                    ('USA_KS','KS','USA','Kansas, USA'),
                    ('USA_MO','MO','USA','Missouri, USA'),
                    ('USA_OK','OK','USA','Oklahoma, USA')
                ;

                create table vendor_applicant(
                    application_id bigserial primary key ,
                    user_id uuid not null unique references auth_integration (user_id) on delete cascade ,
                    business_name varchar(256) not null unique ,
                    address_one varchar(256) not null ,
                    address_two varchar(256) ,
                    city varchar(128) not null ,
                    zip char(5) not null ,
                    territory_id varchar(10) not null references vendor_approved_territory (territory_id),
                    phone varchar(12) not null ,
                    business_email varchar(256) not null unique ,
                    status char(1) not null default 'N',
                    application_date timestamp not null default current_timestamp
                );
            """,
            reverse_sql="""
                drop table if exists vendor_applicant;
                drop table if exists vendor_approved_territory;
            """
        )
    ]
