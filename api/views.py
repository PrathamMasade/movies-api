from collections import Counter
from os import getenv
from uuid import UUID

import requests
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Movies, MoviesCollection, RequestCount
from .serializers import UserSerializer, MovieCollectionSerializer
from requests.auth import HTTPBasicAuth
from .utils import extract_movies_from_collections, get_top_genres


# Feeding the uname and pass of the external api to the environment varaibles
load_dotenv("C:\\Users\\prath\\OneDrive\\Desktop\\movie_api\\api\\client.env")
uname=getenv("client_username")
upass=getenv("client_password")

@api_view(['POST'])
def register(request):

    serializer= UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        user=User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token=Token.objects.create(user=user)
        return Response({"token":token.key})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def movies(request):
    response = requests.get(
        'https://demo.credy.in/api/v1/maya/movies/', 
         auth=HTTPBasicAuth(uname, upass),
        verify= False
    )
    data = response.json()  
    return Response(data)

@api_view(['GET','POST'])
def collection(request):

    if request.method=='POST':
        serializer = MovieCollectionSerializer(data=request.data)

        if serializer.is_valid(): 
            movies_data = serializer.validated_data['movies']  
            movie_instances=[]

            for movie_data in movies_data:
                print(movie_data)
                movie, created = Movies.objects.get_or_create( #we use get_or_create to prevent redundancies
                    uuid=movie_data['uuid'],  #we can use the uuid to check the availability
                    title= movie_data['title'],
                    description= movie_data['description'],
                    genres= movie_data['genres']
                )

                movie_instances.append(movie)

            #saving into the collections
            collection = MoviesCollection.objects.create(
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
            )
            collection.movies.set(movie_instances)
            return Response({"collection_uuid": collection.uuid})
    elif request.method=='GET':

        collections=MoviesCollection.objects.all()

        movielist= extract_movies_from_collections(collections)
        top_genres = get_top_genres(movielist)

        response_data={
                "collections":[
                    {
                        "title":c.title,
                        "uuid":str(c.uuid),
                        "description":c.description
                    }
                    for c in collections
                ],
                "favorite_genres":(list([x[0] for x in top_genres]))
        }

        return Response({"is_success":True,"data":response_data})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT','GET','DELETE'])
def collid(request,collection_uuid):

    collection=MoviesCollection.objects.get(uuid=collection_uuid)

    if request.method== 'PUT':
        data=request.data
        #if title is there in the request only then update
        if 'title' in data:
            collection.title = data['title']
        #if description is there only then update
        if 'description' in data:
            collection.description = data['description']
        # If movies are provided in the request only then update the movie list
        if 'movies' in data:
            movies_data = data['movies']
            
            for movie_data in movies_data:
                movie, created = Movies.objects.get_or_create(
                    uuid=movie_data['uuid'],  
                    title= movie_data['title'],
                    description= movie_data['description'],
                    genres= movie_data['genres']
                )
                collection.movies.add(movie)

        collection.save()
        serializer = MovieCollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        serializer = MovieCollectionSerializer(collection)
        return Response(serializer.data)

    elif request.method == 'DELETE': 
        # Now, if for some reason, the delete() fails then
        # MoviesCollection.objects.get(uuid=collection_uuid) will execute
        # so we return unsuccesful delete
        try:
            collection.delete()
            MoviesCollection.objects.get(uuid=collection_uuid)
            return Response({"Delete":"unsuccessful"})
        
        except MoviesCollection.DoesNotExist:
            return Response({"Delete":"successful"})

def get_request_count(request):
    try:
        request_count = RequestCount.objects.get(id=1)
    except RequestCount.DoesNotExist:
        request_count = RequestCount.objects.create(count=0)

    return JsonResponse({"requests": request_count.count})

def reset_request_count(request):
    try:
        request_count = RequestCount.objects.get(id=1)
    except RequestCount.DoesNotExist:
        request_count = RequestCount.objects.create(count=0)
    request_count.count = 0
    request_count.save()
    return JsonResponse({"message": "Request count reset successfully"})