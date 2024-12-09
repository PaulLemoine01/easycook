from django.contrib import admin

from application.models import Influenceur, Recette, Ingredient, Video


@admin.register(Influenceur)
class InfluenceurAdmin(admin.ModelAdmin):
    list_display = ('instagram_username', )
    search_fields = ('instagram_username', )


@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('nom_singulier',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('instagram_id',)