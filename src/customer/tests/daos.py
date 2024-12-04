import decimal 
import uuid 
from django.test import TestCase
from app import connections
import customer.daos as daos 

class GetShoppingCartDAOTests(TestCase): 
    def __setup_get_shopping_cart(self):
        vendor_user_id = uuid.uuid4()
        user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');
                        
                insert into auth_integration(user_id, email)
                values (%(user_id)s, 'timo@org'); 

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, description ,initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name','description',10.00),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name','description',20.00),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name','description',30.00);

                insert into shopping_cart (user_id, product_id, quantity)
                values (%(user_id)s, 1, 1);
            """, {'vendor_user_id': vendor_user_id, 'user_id': user_id})
        return user_id; 

            
    def test_get_shopping_cart(self):
        #setup
        userid = self.__setup_get_shopping_cart()
        #execute
        cart = daos.get_shopping_cart(userid)
        #assert
        self.assertEqual(cart[0].product_id, 1)
        self.assertEqual(cart[0].quantity, 1)
    
class UpdateShoppingCartDAOTests(TestCase):
    def __setup_update_shopping_cart(self):
        vendor_user_id = uuid.uuid4()
        user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute("""
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');
                        
                insert into auth_integration(user_id, email)
                values (%(user_id)s, 'timo@org'); 

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, description ,initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name','description',10.00),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name','description',20.00),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name','description',30.00);

                insert into shopping_cart (user_id, product_id, quantity)
                values (%(user_id)s, 1, 1);
            """, {'vendor_user_id': vendor_user_id, 'user_id': user_id})
            return user_id
            
    def test_update_shopping_cart(self):
        #setup
        userid = self.__setup_update_shopping_cart()
        #execute
        daos.update_shopping_cart(userid, [(1, 2), (2, 3)])
        #assert
        cart = daos.get_shopping_cart(userid)
        self.assertEqual(cart[0].quantity, 2)
        self.assertEqual(cart[1].quantity, 3)


class ResetShoppingCartDaoTests(TestCase):
    def __setup_reset_shopping_cart(self):
        vendor_user_id = uuid.uuid4()
        user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute(""" 
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');
                        
                insert into auth_integration(user_id, email)
                values (%(user_id)s, 'timo@org'); 

                insert into vendor
                    (vendor_id, user_id, business_name, business_email, phone,
                    address_one, city, zip, territory, approved_by)
                values
                    (1, %(vendor_user_id)s, 'Business Name', 'vendor@morriswa.org', '1231231234',
                    'address line 1', 'city', '55555', 'USA_MO', %(vendor_user_id)s);

                insert into vendor_product
                    (product_id, vendor_id, listed_by, product_name, description ,initial_price)
                values
                    (1, 1, %(vendor_user_id)s, 'Product 1 Name','description',10.00),
                    (2, 1, %(vendor_user_id)s, 'Product 2 Name','description',20.00),
                    (3, 1, %(vendor_user_id)s, 'Product 3 Name','description',30.00);

                insert into shopping_cart (user_id, product_id, quantity)
                values (%(user_id)s, 1, 1);
            """, {'vendor_user_id': vendor_user_id, 'user_id': user_id})
            return user_id
        
    def test_reset_shopping_cart(self):
        #setup
        userid = self.__setup_reset_shopping_cart()
        #execute
        daos.reset_shopping_cart(userid)
        #assert
        cart = daos.get_shopping_cart(userid)
        self.assertEqual(len(cart), 0)

class GetCustomerPreferences(TestCase):
    def __setup_get_customer_preferences(self):
        vendor_user_id = uuid.uuid4()
        user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute(""" 
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');
                        
                insert into auth_integration(user_id, email)
                values (%(user_id)s, 'timo@org'); 
                        
                insert into customer_preferences (user_id, 
                    p_cb_strength_mild,
                    p_cb_strength_med,
                    p_cb_strength_bold,
                    p_cb_strength_blonde,
                    p_cb_caf,
                    p_cb_decaf,
                    p_cb_flavored,
                    p_cb_origin_single,
                    p_cb_origin_blend,
                    n_newsletter_subscription)
                values (%(user_id)s, 'y', 'n', 'n', 'y', 'n', 'y', 'y', 'y', 'n', 'y');
            """, {'vendor_user_id': vendor_user_id, 'user_id': user_id})
        return user_id
        
    def test_get_customer_preferences(self):
        #setup
        userid = self.__setup_get_customer_preferences()
        #execute
        preferences = daos.get_customer_preferences(userid)
        #assert
        self.assertEqual(preferences.strength_mild, 'y')
        self.assertEqual(preferences.strength_med, 'n')
        self.assertEqual(preferences.strength_bold, 'n')
        self.assertEqual(preferences.blonde, 'y')
        self.assertEqual(preferences.caffinated, 'n')
        self.assertEqual(preferences.decaf, 'y')
        self.assertEqual(preferences.flavored, 'y')
        self.assertEqual(preferences.single_origin, 'y')
        self.assertEqual(preferences.origin_blend, 'n')
        self.assertEqual(preferences.newsletter_subscription, 'y')

class UpdateCustomerPreferences(TestCase):
    def __setup_update_customer_preferences(self):
        vendor_user_id = uuid.uuid4()
        user_id = uuid.uuid4()
        with connections.cursor() as cur:
            cur.execute(""" 
                insert into auth_integration (user_id, email)
                values (%(vendor_user_id)s, 'vendor@morriswa.org');
                        
                insert into auth_integration(user_id, email)
                values (%(user_id)s, 'timo@org'); 
                        
                insert into customer_preferences (user_id, 
                    p_cb_strength_mild,
                    p_cb_strength_med,
                    p_cb_strength_bold,
                    p_cb_strength_blonde,
                    p_cb_caf,
                    p_cb_decaf,
                    p_cb_flavored,
                    p_cb_origin_single,
                    p_cb_origin_blend,
                    n_newsletter_subscription)
                values (%(user_id)s, 'y', 'n', 'n', 'y', 'n', 'y', 'y', 'y', 'n', 'y');
            """, {'vendor_user_id': vendor_user_id, 'user_id': user_id})
        return user_id
    
    def test_update_customer_preferences(self):
        # Setup
        user_id = self.__setup_update_customer_preferences()
        # Execute
        preferences = daos.get_customer_preferences(user_id)
        daos.update_customer_preferences(user_id, preferences)

        self.assertEqual(preferences.strength_mild, 'y')
        self.assertEqual(preferences.strength_med, 'n')
        self.assertEqual(preferences.strength_bold, 'n')
        self.assertEqual(preferences.blonde, 'y')
        self.assertEqual(preferences.caffinated, 'n')
        self.assertEqual(preferences.decaf, 'y')
        self.assertEqual(preferences.flavored, 'y')
        self.assertEqual(preferences.single_origin, 'y')
        self.assertEqual(preferences.origin_blend, 'n')
        self.assertEqual(preferences.newsletter_subscription, 'y')
