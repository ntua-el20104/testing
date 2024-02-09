from django.shortcuts import render
from django.http import JsonResponse
from django.template import loader 
from django.http import HttpResponse
from .models import Names,Movies,Crews,Episode,Ratings

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def login(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render())

def names(request):
    names = Names.objects.all().order_by('primaryName').values() 
    template = loader.get_template('names.html')
    context = {
        'names': names
    }
    return HttpResponse(template.render(context, request))

def search_names(request):
    name_query = request.GET.get('query', '')
    if name_query:
        names = Names.objects.filter(primaryName__icontains=name_query)
    else:
        names = Names.objects.none()  # Return an empty queryset if no query
    return render(request, 'search_names.html', {'names': names})

def name_details(request, nconst):
  person = Names.objects.get(nconst=nconst)
  template2 = loader.get_template('my_custom_filters.py')

  try:
      personTitles = Principals.objects.filter(nconst=nconst)
      nameTitles = [(f"titleID: {x.tconst}", f"category: {x.category}") for x in personTitles]
  except personTitles.DoesNotExist:
      personTitles = None
      nameTitles = None


  if person.img_url_asset == None :
    full_url = None
  else:
    baseurl = person.img_url_asset
    width = "w220_and_h330_face"
    full_url = baseurl.replace("{width_variable}", width)

  template = loader.get_template('name_details.html')
  
  nameObject = {
    'person': person,
    'nameID':person.nconst,
    'name':person.primaryName,
    'namePoster': full_url,
    'birthYr':person.birthYear,
    'deathYr':person.deathYear,
    'profession':person.primaryProfession,
    'nameTitles':nameTitles
    }
  return HttpResponse(template.render(nameObject, request))

def titles(request):
    titles = Movies.objects.all().order_by('primaryTitle').values() 
    template = loader.get_template('titles.html')
    context = {
        'titles': titles
    }
    return HttpResponse(template.render(context, request))

def search_titles(request):
    title_query = request.GET.get('query', '')
    if title_query:
        movies = Movies.objects.filter(primaryTitle__icontains=title_query)
    else:
        movies = Movies.objects.none()  # Return an empty queryset if no query
    return render(request, 'search_titles.html', {'movies': movies})

def title_details(request, tconst):
  try:  
    title = Movies.objects.get(tconst=tconst)
    template = loader.get_template('title_details.html')
    
    try:
        rating = Ratings.objects.get(tconst=tconst)
        rating_object = (f"Average Rating: {rating.averageRating}",f"Number of Votes: {rating.numVotes}" )
    except Ratings.DoesNotExist:
        rating = None
        rating_object = None

    try:
        akas = Akas.objects.filter(titleId=tconst)
        akas_titles = [(f"title: {entry.title}", f"region: {entry.region}") for entry in akas]

    except Akas.DoesNotExist:
        akas = None
        akas_titles = None
    
    try:
        # Assuming you've already fetched 'principal' as you've shown:
        principal = Principals.objects.filter(tconst=tconst)

# For each principal, fetch the corresponding person from the Names table and create tuples
        principal_id_and_name = []
        for x in principal:
            try:
                name_entry = Names.objects.get(nconst=x.nconst)
                principal_id_and_name.append(( f"nameId: {x.nconst}" ,f"primary person: {name_entry.primaryName}"  ,f"category: {x.category}"))
            except Names.DoesNotExist:
        # Handle the case where no corresponding entry in Names exists
                name_entry = None
                principal_id_and_name.append((x.nconst, x.category, None))

# Now, principal_id_and_name contains tuples of (nconst, category, primaryName) for each matching entry

    except Principals.DoesNotExist:
        principal = None
    
    if title.img_url_asset == None :
        full_url = None
    else:
        baseurl = title.img_url_asset
        width = "w220_and_h330_face"
        full_url = baseurl.replace("{width_variable}", width)
    
    context = {
        'title': title,
        'image_url': full_url,
        'rating':rating 
    }

    titleObject = {
        'title':title,
        'titleID':title.tconst,
        'primaryTitle':title.primaryTitle,
        'type':title.titleType,
        'originalTitle': title.primaryTitle,
        'titlePoster': full_url,
        'startYear': title.startYear,
        'endYear':title.endYear,
        'genres': title.genres.split(","),
        'titleAkas':akas_titles,
        'principals': principal_id_and_name,
        'rating':rating,
        'rating_object':rating_object
        # 'averageRating': rating.averageRating,
        # 'numVotes':rating.numVotes
    }

    # if request.method == 'GET':
    #return JsonResponse(titleObject)
    # else:
    return HttpResponse(template.render(titleObject,request))
  except Movies.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)

from django.template.loader import render_to_string






def upload(request):
    template = loader.get_template('upload.html')
    return HttpResponse(template.render())





from MySQLdb import IntegrityError
from django.http import JsonResponse
import csv
from .forms import *
from .models import *
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.db import DatabaseError
from django.contrib.auth.models import User
# from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError


# /////////////////////////////// TITLE Names ///////////////////////////////////////

def ProcessTitleNamesTSV(request, file, reset = False):
    reader = csv.reader(file, delimiter='\t')

    ignore_first_line = True
    for row_number, row in enumerate(reader, start=1):
        if ignore_first_line:
            ignore_first_line = False
            continue
        
        tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres, img_url_asset = row
        
        startYear = None if startYear == '\\N' else startYear
        endYear = None if endYear == '\\N' else endYear
        runtimeMinutes = None if runtimeMinutes == '\\N' else runtimeMinutes
        isAdult = None if isAdult == '\\N' else isAdult
        genres = None if genres == '\\N' else genres
        img_url_asset = None if img_url_asset == '\\N' else img_url_asset
        
        # Use get_or_create to insert a new element
        # into the table if not already existed
        try:
            title_obj, created = Names.objects.get_or_create(
                tconst=tconst,
                defaults={
                    'titleType': titleType,
                    'primaryTitle': primaryTitle,
                    'originalTitle': originalTitle,
                    'isAdult': isAdult,
                    'startYear': startYear,
                    'endYear': endYear,
                    'runtimeMinutes': runtimeMinutes,
                    'genres': genres,
                    'img_url_asset': img_url_asset,
                }
            )

            if created:
                print(f"Created new record for tconst: {tconst}")
                # if reset == False:
                #     UploadTitleObject(request, Names.objects.filter(tconst=tconst))
            else:
                print(f"Record for tconst {tconst} already exists, skipping.")

        except Names.MultipleObjectsReturned:
            print(f"Multiple records found for tconst: {tconst}, skipping.")

        print(f"Processed row number: {row_number-1}")
    return row_number-1

def UploadTitleNames(request):
    if request.method == 'POST':
        superuser_token = User.objects.filter(is_superuser=True).values_list('auth_token', flat=True).first()
        token = request.META.get('HTTP_AUTHORIZATION')
        print(superuser_token)
        print(token)

        # Check if the authenticated user is a superuser
        if token == superuser_token:
            form = BasicForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['tsv_file']
                decoded_file = file.read().decode('utf-8').splitlines()
                rows = ProcessTitleNamesTSV(request, decoded_file)
                return JsonResponse({'status': 'success', 'processed_rows': rows})
            else:
                return JsonResponse({'status': 'error', 'message': 'Form is not valid'}, status=400)
        else:
            return JsonResponse({'detail': 'Permission denied. You don\'t have administrator privileges.'}, status=403)
    else:
        form = BasicForm()
        return render(request, 'upload.html', {'form': form})


def ResetTitleNames(request):
    Names.objects.all().delete()
    specific_file_path = '..\\..\\Database\\Data\\truncated_title.Names.tsv'
    with open(specific_file_path, 'r', encoding='utf-8') as file:
        rows = ProcessTitleNamesTSV(request, file, True)
    return JsonResponse({'status': 'success', 'processed_rows': rows})