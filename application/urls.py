from django.urls import path

from application import views
from application.models import Influenceur, Video, Ingredient, Recette, Tag
from customtools.views import generic_url_router

app_name = 'application'

urlpatterns = [
    path("influenceur/refresh/videos", views.ActualiserVideos.as_view(), name="influenceur-refresh-videos"),
    path("analyse/video", views.AnalyseVideo.as_view(), name="analyse-video"),
    path("recette/detail/<uuid:uuid>/", views.RecetteDetail.as_view(), name="recette-detail"),

    #API
    path("api/application/test-response/", views.test_response, name="generate_response"),
    path("api/application/hello_world/", views.hello_world, name="hello"),
    # path("dummy-endpoint/", views.dummy_endpoint, name="dummy_endpoint"),
]

urlpatterns += generic_url_router(model=Influenceur)
urlpatterns += generic_url_router(model=Video)
urlpatterns += generic_url_router(model=Ingredient)
urlpatterns += generic_url_router(model=Recette)
urlpatterns += generic_url_router(model=Tag)
