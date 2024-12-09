import requests
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management import BaseCommand
import random
from bs4 import BeautifulSoup

from application.models import Ingredient


class Command(BaseCommand):
    help = "Tâche automatisée de création de faux utilisateurs pour tester l'application"

    def handle(self, *args, **options):
        urls = [
            "https://www.academiedugout.fr/ingredients/famille/legumes_763",
            "https://www.academiedugout.fr/ingredients/famille/fruits_342",
            "https://www.academiedugout.fr/ingredients/famille/viandes-volailles-et-charcuteries_739",
            "https://www.academiedugout.fr/ingredients/famille/poissons-et-fruits-de-mer_793",
            "https://www.academiedugout.fr/ingredients/famille/oeuf_775",
            "https://www.academiedugout.fr/ingredients/famille/pates-riz-graines-cereales-et_785",
            "https://www.academiedugout.fr/ingredients/famille/epices-huiles-et-condiments_749",
            "https://www.academiedugout.fr/ingredients/famille/chocolats-et-produits-sucres_744",
            "https://www.academiedugout.fr/ingredients/famille/boissons_370"
        ]
        for url in urls:
            response = requests.get(url + "?page=1")
            page_number = 1
            while response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.find_all('div', class_='grid__item one-half lap-one-third desk-one-sixth')
                for item in items:
                    img_tag = item.find_all('span', class_='js-image-lap-and-up')[0]
                    img_url = img_tag['data-src'] if img_tag else 'No image'
                    span_tag = item.find('a')
                    ingredient_name = span_tag.text.strip() if span_tag else ''
                    print(ingredient_name, img_url)
                    if img_url and ingredient_name:
                        ingredient, created = Ingredient.objects.get_or_create(nom_singulier=ingredient_name)
                        if created:
                            ingredient.save()
                            response = requests.get(f"https://www.academiedugout.fr/{img_url}")
                            if response.status_code == 200:
                                img_temp = NamedTemporaryFile(delete=True)
                                img_temp.write(response.content)
                                img_temp.flush()
                                ingredient.photo.save(f'{ingredient_name}.jpg', File(img_temp), save=True)
                response = requests.get(url+f"?page={page_number + 1}")
                page_number += 1
