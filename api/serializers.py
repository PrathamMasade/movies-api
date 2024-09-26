from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movies,MoviesCollection

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model= User
        fields=['username','password']

class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Movies
        fields = ['title', 'description', 'genres', 'uuid']

class MovieCollectionSerializer(serializers.ModelSerializer):
    movies=MovieSerializer(many=True)

    class Meta:
        model = MoviesCollection
        fields = ['uuid','title', 'description', 'movies']