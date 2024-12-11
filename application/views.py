import json
import time
from typing import Dict
from urllib.parse import quote

import httpx
import jmespath
import requests
from django.contrib import messages
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse

from application.models import Influenceur, Video, Recette, Etape
from customtools.views import GenericUpdateView
import os
from dotenv import load_dotenv

class RecetteUpdate(GenericUpdateView):
    model = Recette
    def form_valid(self, form):
        form.instance.etapes.all().delete()
        etapes = []
        for etape in self.request.POST.getlist('etape'):
            Etape()

        return super().form_valid(form)


class InfluenceurCreate(CreateView):
    """
    Create a video
    """
    model = Influenceur
    permission_required = 'application.add_influenceur'
    fields = ["instagram_username"]
    success_message = 'Influenceur created'
    template_name = 'generic_form.html'

    @staticmethod
    def scrape_user(username: str):
        """Scrape Instagram user's data"""
        client = httpx.Client(
            headers={
                "x-ig-app-id": "936619743392459",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
            }
        )
        result = client.get(
            f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
        )
        data = json.loads(result.content)
        return data["data"]["user"]

    def form_valid(self, form):
        username = form.cleaned_data['instagram_username']
        data = self.scrape_user(username)
        influenceur = form.instance
        influenceur.instagram_id = data["id"]
        influenceur.biographie = data["biography"]
        influenceur.nb_followers = data["edge_followed_by"]["count"]
        influenceur.nb_recettes = 0
        influenceur.save()
        response = requests.get(data["profile_pic_url"])
        if response.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)
            img_temp.flush()
            influenceur.photo_profil.save(f'{username}.jpg', File(img_temp), save=True)
            print("Image téléchargée et enregistrée dans la base de données.")
        else:
            print(f"Erreur lors du téléchargement : {response.status_code}")

        messages.success(self.request, self.success_message)


        return redirect('application:influenceur-update', influenceur.uuid)

def hello_world(request):
    print(request.POST.get("id"))
    return HttpResponse("Hello, World!")

@api_view(["POST"])
def test_response(request):
    """
    Endpoint that takes a user message as input and returns a response in JSON format.
    """
    # Placeholder response structure
    base_response = {
        "text": "Hey, test test was successful !",
    }

    return Response(base_response, status=200)

def parse_post(data: Dict) -> Dict:
    result = jmespath.search("""{
        id: id,
        shortcode: shortcode,
        dimensions: dimensions,
        src: display_url,
        src_attached: edge_sidecar_to_children.edges[].node.display_url,
        has_audio: has_audio,
        video_url: video_url,
        views: video_view_count,
        plays: video_play_count,
        likes: edge_media_preview_like.count,
        location: location.name,
        taken_at: taken_at_timestamp,
        related: edge_web_media_to_related_media.edges[].node.shortcode,
        type: product_type,
        video_duration: video_duration,
        music: clips_music_attribution_info,
        is_video: is_video,
        tagged_users: edge_media_to_tagged_user.edges[].node.user.username,
        captions: edge_media_to_caption.edges[].node.text,
        related_profiles: edge_related_profiles.edges[].node.username,
        comments_count: edge_media_to_parent_comment.count,
        comments_disabled: comments_disabled,
        comments_next_page: edge_media_to_parent_comment.page_info.end_cursor,
        comments: edge_media_to_parent_comment.edges[].node.{
            id: id,
            text: text,
            created_at: created_at,
            owner: owner.username,
            owner_verified: owner.is_verified,
            viewer_has_liked: viewer_has_liked,
            likes: edge_liked_by.count
        }
    }""", data)
    return result
def scrape_user_posts(influenceur, session: httpx.Client, page_size=12, max_pages: int = None):
    user_id = influenceur.instagram_id
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": page_size,
        "after": None,
    }
    _page_number = 1
    while True:
        print(f"Page {_page_number}")
        resp = session.get(base_url + quote(json.dumps(variables)))
        data = resp.json()
        posts = data["data"]["user"]["edge_owner_to_timeline_media"]
        for post in posts["edges"]:
            yield parse_post(post["node"])
        page_info = posts["page_info"]
        if _page_number == 1:
            print(f"scraping total {posts['count']} posts of {influenceur.instagram_username}")
        else:
            print(f"scraping page {_page_number}")
        if not page_info["has_next_page"]:
            break
        if variables["after"] == page_info["end_cursor"]:
            break
        variables["after"] = page_info["end_cursor"]
        _page_number += 1
        if max_pages and _page_number > max_pages:
            break

class ActualiserVideos(View):
    def get(self, request, *args, **kwargs):
        influenceur = Influenceur.objects.get(uuid=request.GET.get("influenceur_uuid"))
        with httpx.Client(timeout=httpx.Timeout(20.0)) as session:
            print("Beginning scrapping")
            data = list(scrape_user_posts(influenceur, session, max_pages=3))
            print("beginning saving")
            for data_video in data:
                if data_video["video_url"]:
                    video, created = Video.objects.get_or_create(instagram_id=data_video["id"], instagram_shortcode=data_video["shortcode"])
                    video.influenceur = influenceur
                    video.nb_vue = data_video["views"]
                    video.nb_likes = data_video["likes"]
                    video.description = data_video["captions"][0]
                    video.url = data_video["video_url"]
                    video.save()
                    total = time.time()
                    response = requests.get(data_video["src"])
                    if response.status_code == 200 and created:
                        img_temp = NamedTemporaryFile(delete=True)
                        img_temp.write(response.content)
                        img_temp.flush()
                        video.photo.save(f'{data_video["id"]}.jpg', File(img_temp), save=True)
                        print("download photo:", total-time.time())
                    else:
                        print(f"Erreur lors du téléchargement : {response.status_code}")
        return redirect(reverse("application:influenceur-update", kwargs={"uuid": influenceur.uuid}))


class AnalyseVideo(View):
    def get(self, request, *args, **kwargs):
        print(self.request.GET.get('video_uuid'))
        video_uuid = self.request.GET.get('video_uuid')
        call_command('analyse_video', video_uuid, verbosity=1)

        return redirect(reverse("application:influenceur-list"))

class RecetteDetail(DetailView):
    model = Recette
    template_name = "application/recette_detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"


# @api_view(["POST"])
# def dummy_endpoint(request):
#     """
#     Endpoint that takes a user message as input and returns a response in JSON format.
#     """
#     # Placeholder response structure
#     base_response = {
#         "text": "Hey, test test was successful !",
#     }

#     return Response(base_response, status=200)
