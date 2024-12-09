import json
import os

import openai
import requests
import speech_recognition as sr
from django.core.management import BaseCommand
from django.db import transaction
from moviepy.video.io.VideoFileClip import VideoFileClip

from application.models import Video, Tag, Ingredient, Quantite, Etape, Recette


def download_video(video_url):
    response = requests.get(video_url, stream=True)
    filename = f"video.mp4"
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Vidéo téléchargée et enregistrée sous {filename}")
    else:
        print(f"Erreur lors du téléchargement : {response.status_code}")


def extract_audio(video_file):
    video_clip = VideoFileClip(video_file)
    audio_clip = video_clip.audio
    return audio_clip


def build_recipe(description, speech):
    client = openai.OpenAI(
        organization=os.getenv("OPENAI_ORGANIZATION"),
        project=os.getenv("OPENAI_PROJECT"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    instructions = f"""
                Ton objectif est de recréer des recettes de cuisines à partir de vidéos format Short, Réeels instagram. 
                Pour cela, l'utilisateur va t'envoyer à la fois l'audio de la vidéo sous forme de texte (transcription), ainsi que la description de la vidéo.

                A partir des informations transmises, il faut recréer la recette de la vidéo.
                Tu es donc un chef cuisiner et tu as écrit de nombreux livres de recettes tout au long de tavie. Cela fait plus de 20 ans que tu travaille dans ce domaine. Ton objectif est de créer des recettes les mieux organisées, simple à comprendre et facile à refaire.
                Il faudra aussi faire une estimation des quantitées et du nombre de personne si ce n'est pas précisé. La recette obtenu sera la plus complète possible.
                Exemple de quantités: [{{"ingredient": "tomates", "quantite": 3, "unite": "}}, {{"ingredient": "sucre", "quantite": 3, "unite": "cuillères à soupe"}}, {{"ingredient": "sel", "quantite": 1, "unite": "pincée"}}, {{"ingredient": "farine", "quantite": 300, "unite":"g" ...}}            

                Il faudra aussi caractériser la recettes avec des tags. Les tags ne doivent pas être des ingredients. Maximum 3 tags.
                Exemple de tags: végétarien, entrée, plat, dessert, végétalien, végan ...

                Voici le format à respecter:
                {{
                "nom": Nom de la recette
                "ingredients": [ingredient1: quantité ingredient1, ingredient2: quantite ingredient2 ...],
                "nb_personnes": estimation du nombre de personne  
                "etapes": [etape1, etape2, ...],
                "tags": [tag1, tag2, ...],
                }}
                """
    messages = [
        {
            'role': 'system',
            'content': instructions,
        },
        {"role": "user",
         "content": f"""
                     Voici la transcription de la vidéo: {speech}

                    Voici la description de la vidéo: {description}
                    """
         }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return json.loads(response.choices[0].message.content)


def get_speech(video_url):
    download_video(video_url)
    audio = extract_audio("video.mp4")
    audio_output_path = "extracted_audio.wav"
    audio.write_audiofile(audio_output_path, codec="pcm_s16le")
    r = sr.Recognizer()
    recette = sr.AudioFile('extracted_audio.wav')
    with recette as source:
        audio = r.record(source)
    speech = r.recognize_google(audio, language="fr-FR")
    return speech


class Command(BaseCommand):
    help = "Tâche automatisée de création de faux utilisateurs pour tester l'application"

    def add_arguments(self, parser):
        parser.add_argument('video_uuid', type=str, help='Uuid de la vidéo')

    def handle(self, *args, **options):
        video = Video.objects.get(uuid=options["video_uuid"])
        speech = get_speech(video.url)
        recette_data = build_recipe(video.description, speech)

        with transaction.atomic():  # Utilise une transaction pour garantir l'intégrité de l'enregistrement
            # Création des tags
            tag_objects = []
            for tag_name in recette_data['tags']:
                tag, created = Tag.objects.get_or_create(nom=tag_name)
                tag_objects.append(tag)

            # Création des ingrédients et quantités
            quantite_objects = []
            for ingredient_data in recette_data['ingredients']:
                ingredient_name = ingredient_data['ingredient']
                ingredient, created = Ingredient.objects.get_or_create(
                    nom_singulier=ingredient_name,
                    defaults={'nom_pluriel': ingredient_name + 's'}  # Exemple de nom pluriel
                )

                quantite = Quantite.objects.create(
                    ingredient=ingredient,
                    quantite=ingredient_data['quantite'],
                    unite_mesure=ingredient_data['unite']
                )
                quantite_objects.append(quantite)

            # Création des étapes
            etape_objects = []
            for ordre, content in enumerate(recette_data['etapes'], start=1):
                etape = Etape.objects.create(
                    ordre=ordre,
                    content=content
                )
                etape_objects.append(etape)

            # Création de la recette
            recette = Recette.objects.create(
                nom=recette_data['nom'],
                nb_personnes=recette_data['nb_personnes'],
                video_id=video.id
            )

            # Ajout des relations ManyToMany
            recette.quantites.set(quantite_objects)
            recette.etapes.set(etape_objects)
            recette.tags.set(tag_objects)
            recette.save()

        print(recette)
