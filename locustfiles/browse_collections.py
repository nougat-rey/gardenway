from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):

    # Tasks to execute
    #   - viewing collections
    #   - viewing collection details

    wait_time = between(1, 5)

    @task(1)
    def view_collections(self):
        self.client.get(f'/store/collections', name='/store/collections')

    @task(4)
    def view_collection(self):
        collection_id = randint(1, 5)
        self.client.get(
            f'/store/collections/{collection_id}', name='/store/collections/:id')
