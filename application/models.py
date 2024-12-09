import uuid
from django.db import models
from django.urls import reverse


class Ingredient(models.Model):
    nom_singulier = models.CharField(max_length=30, null=False, blank=False)
    nom_pluriel = models.CharField(max_length=30, null=False, blank=False)
    photo = models.ImageField(upload_to='ingredients/', null=True, blank=True)

    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

class Influenceur(models.Model):
    photo_profil = models.ImageField(upload_to='profils/', null=True)
    instagram_id = models.CharField(max_length=30, null=False, blank=False, verbose_name="Instagram ID")
    instagram_username = models.CharField(max_length=30, null=False, blank=False, verbose_name="Instagram username")
    biographie = models.TextField(null=False, blank=False, verbose_name="Bio")
    nb_followers = models.IntegerField(verbose_name="Followers")

    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def get_absolute_url(self):
        return reverse('application:influenceur-detail', args=(self.uuid,))

    def get_update_url(self):
        return reverse('application:influenceur-update', args=(self.uuid,))

    def get_list_url(self):
        return reverse('application:influenceur-update', args=(self.uuid,))

    def get_delete_url(self):
        return reverse('application:influenceur-delete', args=(self.uuid,))

    def __str__(self):
        return self.instagram_username


class Etape(models.Model):
    ordre = models.IntegerField(null=False, blank=False, verbose_name="Ordre")
    content = models.TextField(null=False, blank=False, verbose_name="Contenu de l'étape")

    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def __str__(self):
        return f"{self.ordre}- {self.content}"

class Quantite(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)
    quantite = models.CharField(max_length=30, null=False, blank=False, verbose_name="Quantité")
    unite_mesure = models.CharField(max_length=30, null=False, blank=False, verbose_name="")

    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def __str__(self):
        return f"{self.quantite} {self.unite_mesure} de {self.ingredient.nom_singulier}"

class Tag(models.Model):
    nom = models.CharField(max_length=30, null=False, blank=False, verbose_name="")

    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    def __str__(self):
        return self.nom

class Recette(models.Model):
    nom = models.CharField(max_length=70, null=False, blank=False, verbose_name="Nom")
    video = models.OneToOneField("Video", verbose_name="Vidéo", on_delete=models.SET_NULL, null=True, blank=True, related_name="recette")
    tags = models.ManyToManyField(Tag, verbose_name="tags")
    nb_personnes = models.IntegerField(verbose_name="Nombre de personnes", null=True, blank=True)

    quantites = models.ManyToManyField(Quantite, verbose_name="Quantités")
    etapes = models.ManyToManyField(Etape, verbose_name="Etapes")

    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def get_absolute_url(self):
        return reverse('application:recette-detail', args=(self.uuid,))

    def get_update_url(self):
        return reverse('application:recette-update', args=(self.uuid,))

    def get_list_url(self):
        return reverse('application:recette-update', args=(self.uuid,))

    def get_delete_url(self):
        return reverse('application:recette-delete', args=(self.uuid,))

    def __str__(self):
        return self.nom


class Video(models.Model):
    photo = models.ImageField(upload_to='videos', null=True, blank=True)
    influenceur = models.ForeignKey(Influenceur, on_delete=models.SET_NULL, null=True)
    url = models.URLField()
    instagram_id = models.CharField(max_length=30, unique=True)
    instagram_shortcode = models.CharField(max_length=30, unique=True)
    nb_vue = models.IntegerField(verbose_name="Vues", null=True, blank=True)
    nb_likes = models.IntegerField(verbose_name="Likes", null=True, blank=True)
    description = models.TextField(null=False, blank=False, verbose_name="Description")


    created_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
        verbose_name='Date de création'
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        auto_now_add=False,
        verbose_name='Update date'
    )

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def get_absolute_url(self):
        return reverse('application:video-detail', args=(self.uuid,))

    def get_update_url(self):
        return reverse('application:video-update', args=(self.uuid,))

    def get_list_url(self):
        return reverse('application:video-update', args=(self.uuid,))

    def get_delete_url(self):
        return reverse('application:video-delete', args=(self.uuid,))

    class Meta:
        ordering = ['-created_date']


