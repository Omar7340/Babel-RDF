from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


SITE_NAME = "Babel"

# Page Home
def index(request):
    template = loader.get_template('index.html')
    context = {
        'title': SITE_NAME
    }
    return HttpResponse(template.render(context, request))

# Page Manga List
def manga_list(request):
    template = loader.get_template('pages/list_mangas.html')
    context = {
        'title': SITE_NAME
    }
    return HttpResponse(template.render(context, request))

# Page Manga Details
def manga_details(request, name):
    template = loader.get_template('pages/details_manga.html')
    context = {
        'title': SITE_NAME
    }
    return HttpResponse(template.render(context, request))

# Page Auteur List
def auteurs_list(request):
    template = loader.get_template('pages/list_auteurs.html')
    context = {
        'title': SITE_NAME
    }
    return HttpResponse(template.render(context, request))

# Page Auteur Details
def auteur_details(request, name):
    template = loader.get_template('pages/details_auteur.html')
    context = {
        'title': SITE_NAME
    }
    return HttpResponse(template.render(context, request))


# Custom page 404
def error404(request, exeption):
    context = {
        'title': SITE_NAME
    }
    return render(request, 'error-404.html', context, status=404)