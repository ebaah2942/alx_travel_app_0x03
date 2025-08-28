from django.core.management.base import BaseCommand
from listings.models import Listing
import random

class Command(BaseCommand):
    help = "Seed database with sample listing data"

    def handle(self, *args, **kwargs):
        titles = ["Beach Villa", "Mountain Cabin", "City Apartment", "Country Cottage"]
        locations = ["Accra", "Kumasi", "Takoradi", "Cape Coast"]

        for i in range(10):
            Listing.objects.create(
                title=random.choice(titles),
                description="A beautiful place to stay.",
                price_per_night=random.randint(100, 500),
                location=random.choice(locations)
            )

        self.stdout.write(self.style.SUCCESS("Seeded 10 listings."))
