import importlib
import re
from datetime import datetime

from django import forms
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, QuerySet
from django.forms import modelform_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, path
from django.views.generic import ListView, DeleteView, UpdateView, CreateView

from customtools.forms import GenericSearchForm, Select2MutipleField
from customtools.mixins import CustomListView, CustomCreateView, CustomUpdateView, CustomDeleteView


class DynamicSearchFormMixin:
    """
    Vue qui permet de gérer automatiquement les filtres sur les colonnes des list view
    Chaque modèle doit avoir une fonction available_list_fields
    Chaque field possède différents paramètres:
        - name (obligatoire): correspond au nom du champs ou de la relation au champs concerné (ex: vehicule, vehicule__equipe__entite ...)
        - verbose_name (obligatoire): Correspond au nom du champs qui sera affiché
        - internal_type (obligatoire): permets de déterminer le type de formulaire que l'on a
        - ordering (obigatoire): sert à savoir si on peut filtrer ou trier sur cette colonne
        - index (facultatif): utile pour la fonctionnalité visible columns
        - visible (facultatif): utile pour la fonctionnalité visible columns
        - additionnal_search_field (facultatif): utile pour ajouter des champs de recherche en plus qui seront toujours affiche (pas forcément de colonne correspondantes)
        - search_initial (facultatif): Permet d'initialiser le formulaire avec une valeur par défaut pour un champs (ex: "search_initial": {"name": "statut_vente__in", "values": [Vehicule.STATUT_VENTE_CHOICES[0][0]]}

    Pour fonctionner, il est nécessaire d'avoir les fichiers dynamic_search_form.html et search_fields.html
    Les fonctions initializeSelect2 et initializeDateRangePicker sont nécessaires dans le fichier custom.js
    La fonction post de la list view doit appeler super si 'column_name' in request.POST


    Check automatiquement si une classe **Model name**Select2 existe dans le fichier views de l'app concernée et utilise l'url select 2 doit être 'app_name:lower_model_name-select2

    """
    def available_list_fields(self):
        """
        Return the list of columns to display in the list view
        """
        available_fields = []
        if hasattr(self.model, "available_list_fields"):
            return self.model.available_list_fields()

        for field in self.model._meta.get_fields():
            if field.name in self.exclude_fields:
                continue
            if not hasattr(field, "verbose_name") or field.name == "modified_date":
                continue
            available_fields.append(
                {
                    "name": field.name,
                    "verbose_name": field.verbose_name,
                    "internal_type": field.get_internal_type(),
                    "visible": True,
                    "ordering": True,
                }
            )
        return available_fields

    def get_available_list_fields(self, request, model):
        """
        Method to quickly get all list fields of a model and determinate which one are visible
        """

        available_list_fields = self.available_list_fields()
        visible_fields = request.session.get(f"{model.__name__.lower()}_list_visible_fields")
        for field in available_list_fields:
            if visible_fields:
                field["visible"] = field["name"] in visible_fields
        return available_list_fields

    def post(self, request, *args, **kwargs):
        form, _ = self.get_search_form(field_name=request.POST.get('column_name'))
        template_form = render_to_string('search_fields.html', context={'dynamic_search_form': form, 'modal': True})
        return JsonResponse({'success': True, 'form': template_form})

    def get_form_field(self, field, fields):
        """
        Cette fonction permet de générer les fields liés à un champs d'un modèle
        Le paramètre field est un dictionnaire de la liste available_fields, il possède donc toutes les caractéristiques définies avant (name, verbose_name, internal_type....)

        exs:
        - Le champs index d'un trajet est un nombre. Deux fields sont alors générés: index__gte et index__lte
        - Le champs vehicule d'un trajet est une ForeignKey et une classe VehiculeSelect2 est présente dans le fichier views.py de l'app trajets, un field vehicule__in sera créé avec un Select2MutipleField
        """
        if field["internal_type"] in ["FloatField", "IntegerField"]:
            fields[f'{field["name"]}__gte'] = forms.FloatField(label=f"{field['verbose_name']} (Supérieur à)", required=False)
            fields[f'{field["name"]}__lte'] = forms.FloatField(label=f"{field['verbose_name']} (Inférieur à)", required=False)
        elif field["internal_type"] in ["ForeignKey", "ManyToOneRel", "ManyToManyField"]:
            next_model = self.model
            for related_field in field["name"].split("__"):
                next_model = next_model._meta.get_field(related_field).related_model
            if importlib.util.find_spec(f"{next_model._meta.app_label}") and hasattr(importlib.import_module(f"{next_model._meta.app_label}.views"),
                                                                                     f"{next_model.__name__}Select2"):
                fields[f'{field["name"]}__in'] = Select2MutipleField(
                    label=field["verbose_name"],
                    url=reverse_lazy(f"{next_model._meta.app_label}:{next_model.__name__.lower()}-select2") + "?template_minimal=true&id=true",
                    placeholder=f"Filtrer par {field['verbose_name'].lower()}",
                    queryset=next_model.objects.all(),
                    required=False,
                )
            else:
                fields[f'{field["name"]}__in'] = forms.ModelMultipleChoiceField(queryset=next_model.objects.all(), required=False, label=field["verbose_name"])
        elif field["internal_type"] in ["CharField", "TextField"]:
            next_model = self.model
            field_name = field["name"]
            if "__" in field["name"]:
                for related_field in field["name"].split("__")[:-1]:
                    next_model = next_model._meta.get_field(related_field).related_model
                    field_name = field["name"].split("__")[-1]
            choices = next_model._meta.get_field(field_name).choices
            if bool(choices):
                fields[f'{field["name"]}__in'] = forms.MultipleChoiceField(choices=choices, required=False, label=field["verbose_name"])
            else:
                fields[f'{field["name"]}__icontains'] = forms.CharField(required=False, label=field["verbose_name"])
        elif field["internal_type"] in ["DateTimeField", "DateField"]:
            fields[f'{field["name"]}'] = forms.CharField(label=field["verbose_name"], required=False,
                                                         widget=forms.DateTimeInput(attrs={'class': 'daterange-picker'}))
        elif field["internal_type"] == "BooleanField":
            CHOICES = ((None, "Je ne sais pas"), (True, "Oui"), (False, "Non"))
            fields[field["name"]] = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=False, label=field["verbose_name"])

    def get_search_form(self, field_name=None):
        """
        Cette fonction permet de générer directement le form de recherche en fonction des paramètres contenus dans l'url
        Elle est à la fois utilisée pour générer le form principal afficher sur la list view mais aussi pour générer le form du modal lorsque l'on click sur l'entête d'une colonne (l'argument field_name sert à préciser le champs généré pour le modal)
        """
        request = self.request.GET.copy()
        fields = {}
        if not field_name:
            fields["query"] = forms.CharField(label="Rechercher", required=False, widget=forms.TextInput(attrs={"placeholder": "Rechercher..."}))
        available_list_fields = self.get_available_list_fields(self.request, self.model)
        for field in available_list_fields:
            if not field_name or field_name == field.get("name"):
                new_fields = {}
                self.get_form_field(field, new_fields)
                for additional_field in field.get("additional_fields", []):
                    self.get_form_field(additional_field, new_fields)
                field["filtered"] = False
                if list(set(self.request.GET.keys()) & set(new_fields.keys())) or self.request.GET.get("order") in [field["name"], f'-{field["name"]}']:
                    field["filtered"] = True
                if "query" not in request.keys() and field.get("search_initial", None):
                    request.setlist(field["search_initial"]["name"], field["search_initial"]["values"])
                if list(set([name for name, value in request.items() if value]) & set(new_fields.keys())) or field.get("additionnal_search_field") or field_name:
                    fields.update(new_fields)
        auto_id = "id_%s__search" if field_name else "id_%s"
        form = type('SearchForm', (forms.BaseForm,), {'base_fields': fields})(request, auto_id=auto_id)
        form.is_valid()
        return form, available_list_fields

    def get_queryset(self):
        """
        Modify the default queryset
        """
        queryset = super().get_queryset()
        self.form, self.available_list_fields = self.get_search_form()
        self.search = self.form.cleaned_data
        order = self.request.GET.get("order")
        if self.search.get("query"):
            text_fields = [field.name for field in self.model._meta.fields if field.get_internal_type() in ["CharField", "TextField"]]
            if hasattr(self.model, "search_fields"):
                text_fields += self.model.search_fields
            terms = [term for term in self.search["query"].split(" ") if term]
            query = Q()
            for term in terms:
                subquery = Q()
                for field in text_fields:
                    subquery |= Q(**{f"{field}__icontains": term})
                query &= subquery
            queryset = queryset.filter(query)
        filters = {}
        for field_name, value in self.search.items():
            if value and field_name != "query":
                pattern = r"^\d{2}/\d{2}/\d{4} - \d{2}/\d{2}/\d{4}$"
                if type(value) == str and re.fullmatch(pattern, value):
                    date_format = "%d/%m/%Y"
                    filters[field_name + '__gte'] = datetime.strptime(self.search.get(field_name).split(' - ')[0], date_format)
                    filters[field_name + '__lte'] = datetime.strptime(self.search.get(field_name).split(' - ')[1], date_format)
                else:
                    filters[field_name] = value
        queryset = queryset.filter(**filters)

        if order:
            try:
                queryset = queryset.order_by(order)
            except FieldDoesNotExist:
                messages.error(self.request, "Ordre incorrect")
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add extra variables in context
        """
        context = super().get_context_data(**kwargs)
        context['dynamic_search_form'] = self.form
        context["available_list_fields"] = self.available_list_fields
        return context


class GenericListView(DynamicSearchFormMixin, ListView):
    search_form_class = GenericSearchForm
    exclude_fields = ["id", "uuid"]
    paginate_by = 30

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        return [
            f"{self.model._meta.model_name}_list.html",
            f"{self.model._meta.app_label}/{self.model._meta.model_name}_list.html",
            "generic_list.html",
        ]

    def get_permission_required(self):
        if self.permission_required:
            return [self.permission_required]
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return [f"{app_label}.view_{model_name}"]


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["verbose_name"] = self.model._meta.verbose_name
        context["verbose_name_plural"] = self.model._meta.verbose_name_plural
        context["create_permission"] = self.request.user.has_perm(f"{self.model._meta.app_label}.add_{self.model._meta.model_name}")
        context["update_permission"] = self.request.user.has_perm(f"{self.model._meta.app_label}.change_{self.model._meta.model_name}")
        context["create_url"] = reverse_lazy(f"{self.model._meta.app_label}:{self.model._meta.model_name}-create")
        return context




class GenericCreateView(CreateView):
    fields = "__all__"
    success_message = "Objet créé"

    def get_template_names(self):
        return [
            f"{self.model._meta.model_name}_form.html",
            f"{self.model._meta.app_label}/{self.model._meta.model_name}_form.html",
            "generic_form.html",
        ]

    def form_valid(self, form):
        for attribute in ["intervenant", "user", "auteur"]:
            if hasattr(self.model, attribute):
                setattr(form.instance, attribute, self.request.user)
        return super().form_valid(form)

    def get_permission_required(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return [f"{app_label}.add_{model_name}"]

    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        return self.request.session[f"{self.model._meta.model_name}_list_url"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["verbose_name"] = self.model._meta.verbose_name
        context["verbose_name_plural"] = self.model._meta.verbose_name_plural
        return context

    def get_form_class(self):
        forms_module = importlib.import_module(f"{self.model._meta.app_label}.forms")
        if hasattr(forms_module, f"{self.model.__name__}Form"):
            form_class = getattr(forms_module, f"{self.model.__name__}Form")
            return form_class
        return modelform_factory(self.model, fields=self.fields)


class GenericUpdateView(UpdateView):
    fields = "__all__"
    success_message = "Informations enregistrées"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            self.model._meta.get_field('uuid')
            uuid_value = self.kwargs.get('uuid')
            if uuid_value:
                return get_object_or_404(queryset, uuid=uuid_value)
        except FieldDoesNotExist:
            pk_value = self.kwargs.get(self.pk_url_kwarg)
            return get_object_or_404(queryset, pk=pk_value)
        return super().get_object(queryset)
    def get_template_names(self):
        return [
            f"{self.model._meta.model_name}_form.html",
            f"{self.model._meta.app_label}/{self.model._meta.model_name}_form.html",
            "generic_form.html",
        ]

    def get_form_class(self):
        forms_module = importlib.import_module(f"{self.model._meta.app_label}.forms")
        if hasattr(forms_module, f"{self.model.__name__}Form"):
            form_class = getattr(forms_module, f"{self.model.__name__}Form")
            return form_class
        return modelform_factory(self.model, fields=self.fields)

    def form_valid(self, form):
        if hasattr(self.object, "intervenant"):
            form.instance.intervenant = self.request.user
        return super().form_valid(form)

    def get_permission_required(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return [f"{app_label}.change_{model_name}"]

    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        return reverse_lazy(f'application:{self.model._meta.model_name}-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delete_permission"] = self.request.user.has_perm(f"{self.model._meta.app_label}.delete_{self.model._meta.model_name}")
        return context


class GenericDeleteView(DeleteView):
    success_message = "Objet supprimées"

    def get_object(self):
        if "uuid" in self.kwargs:
            return self.model.objects.get(uuid=self.kwargs["uuid"])
        return super().get_object()

    def get_template_names(self):
        return [
            f"{self.model._meta.model_name}_confirm_delete.html",
            f"{self.model._meta.app_label}/{self.model._meta.model_name}_confirm_delete.html",
            "generic_confirm_delete.html",
        ]

    def get_permission_required(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return [f"{app_label}.delete_{model_name}"]

    def get_success_url(self):
        return self.model.get_list_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["list_url"] = self.model.get_list_url
        return context


def get_view(model, type):
    views_module = importlib.import_module(f"{model._meta.app_label}.views")
    if hasattr(views_module, f"{model.__name__}{type}"):
        view = getattr(views_module, f"{model.__name__}{type}")
        return view.as_view()
    view = globals()[f"Generic{type}View"]
    return view.as_view(model=model)


def generic_url_router(model):
    """
    Return a list of url patterns for the generic views
    """
    model_name = model.__name__.lower()
    type, name = "int", "pk"
    if getattr(model, "uuid"):
        type, name = "uuid", "uuid"
    return [
        path(f'{model_name}', get_view(model, "List"), name=f"{model_name}-list"),
        path(f'{model_name}/creation/', get_view(model, "Create"), name=f"{model_name}-create"),
        path(f'{model_name}/modification/<{type}:{name}>/', get_view(model, "Update"), name=f"{model_name}-update"),
        path(f'{model_name}/suppression/<{type}:{name}>/', get_view(model, "Delete"), name=f"{model_name}-delete"),
    ]