from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_create_shopping_cart_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- author: Rahul Bhattachan
                CREATE TABLE product_reviews (
                    review_id BIGSERIAL PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES auth_integration(user_id) ON DELETE CASCADE,
                    product_id BIGINT NOT NULL REFERENCES vendor_product(product_id) ON DELETE CASCADE,
                    review_text VARCHAR(10000) NOT NULL,
                    review_score SMALLINT CHECK (review_score >= 1 AND review_score <= 5) NOT NULL
                );
            """,
            reverse_sql="""
                drop table if exists product_reviews;
            """
        )
    ]
