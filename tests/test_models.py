# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product and read it from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_deserialize_product_with_error(self):
        """It should raise and error on deserialize a product"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product_dict = product.serialize()
        # Error on invalid bool value
        product_dict['available'] = "invalid string"
        logging.debug(product_dict)
        with self.assertRaises(DataValidationError):
            product.deserialize(product_dict)

        # Error on no key for price on dict
        product = ProductFactory()
        product_dict = product.serialize()
        del product_dict["description"]
        with self.assertRaises(DataValidationError):
            product.deserialize(product_dict)

        # Error on empty dict
        with self.assertRaises(DataValidationError):
            product.deserialize(None)

    def test_update_a_product(self):
        """It should Update a product and save it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating product
        product = ProductFactory()
        product.id = None
        product.create()
        logging.debug(product)
        # Asserting id is not None
        self.assertIsNotNone(product.id)
        # Updating description
        product.description = "updated description"
        original_id = product.id
        product.update()
        # Asserting updated product
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "updated description")
        # Asserting updated values in db
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "updated description")

    def test_update_with_error(self):
        """It should raise a DataValidationError on update"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating product
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should delete a product"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating product
        product = ProductFactory()
        product.id = None
        product.create()
        # Asserting there is only one product
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Deleting product
        product.delete()
        # Asserting there is no products
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # Asserting there is 5 product
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """It should find a product by name"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # Retrieving first product name
        name = products[0].name
        # Count products by name
        count = len([product for product in products if product.name == name])
        named_products = Product.find_by_name(name)
        self.assertEqual(named_products.count(), count)

        for product in named_products:
            self.assertEqual(product.name, name)

    def test_find_a_product_by_availability(self):
        """It should find a product by availability"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieving first product availabity
        availability = products[0].available
        # Count products by name
        count = len([product for product in products if product.available == availability])
        available_products = Product.find_by_availability(availability)
        self.assertEqual(available_products.count(), count)

        for product in available_products:
            self.assertEqual(product.available, availability)

    def test_find_a_product_by_category(self):
        """It should find a product by category"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieving first product category
        category = products[0].category
        # Count products by category
        count = len([product for product in products if product.category == category])
        categorized_products = Product.find_by_category(category)
        self.assertEqual(categorized_products.count(), count)

        for product in categorized_products:
            self.assertEqual(product.category, category)

    def test_find_a_product_by_price(self):
        """It should find a product by price"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieving first product price
        price = products[0].price
        # Count products by price
        count = len([product for product in products if product.price == price])
        price_products = Product.find_by_price(price)
        self.assertEqual(price_products.count(), count)

        for product in price_products:
            self.assertEqual(product.price, price)

    def test_find_a_product_by_str_price(self):
        """It should find a product by str price"""
        products = Product.all()
        self.assertEqual(products, [])
        # Creating products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieving first product price
        price = products[0].price
        # Count products by price
        count = len([product for product in products if product.price == price])
        price_products = Product.find_by_price(str(price))
        self.assertEqual(price_products.count(), count)

        for product in price_products:
            self.assertEqual(product.price, price)
