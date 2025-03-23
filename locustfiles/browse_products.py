from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):

    # Tasks to execute
    #   - viewing products
    #   - viewing product details

    wait_time = between(1, 5)

    @task(2)
    def view_products(self):
        self.client.get(f'/store/products', name='/store/products')

    @task(4)
    def view_product(self):
        product_id = randint(1, 50)
        self.client.get(
            f'/store/products/{product_id}', name='/store/products/:id')
