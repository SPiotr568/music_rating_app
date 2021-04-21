from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CreateUserForm, ContactForm, ReviewerForm, SongForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from .models import Song, Reviewer, Rating
from operator import attrgetter
from django.db.models import Sum
from rating import settings
import requests
import json
from urllib.parse import urlparse, parse_qs
from django.core.mail import send_mail, BadHeaderError
from django.utils.safestring import mark_safe


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            mail = form.cleaned_data.get('email')
            messages.success(request, 'Account created! Sign in' + username)
            return redirect('login')
    context = {
        'form': form
    }
    return render(request, 'rate/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
    context = {}
    return render(request, 'rate/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def home(request):
    songs = Song.objects.all().order_by('-overall_rating')[:30]
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    for song in songs:
        url = song.url
        url_data = urlparse(url)
        query = parse_qs(url_data.query)
        try:
            video_id = query["v"][0]
            params = {
                'key': settings.YOUTUBE_DATA_API_KEY,
                'part': 'snippet,contentDetails,statistics',
                'id': video_id
            }
            r = requests.get(video_url, params=params)
            results = r.json()['items'][0]
            song.thumbnail = results['snippet']['thumbnails']['default']['url']
            views = int(results['statistics']['viewCount'])
            song.views = f'{views:,}'
        except KeyError:
            song.thumbnail = None
            song.url = ''
            song.views = '-'
    context = {
        'songs': songs[:20],
        'propositions': songs[20:]
    }
    return render(request, 'rate/home.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def song(request, pk):
    song = Song.objects.get(id=pk)

    if request.method == "POST":
        new_rating = request.POST.get('rating')
        if new_rating is not None:
            try:
                rating_from_db = Rating.objects.all().get(song=song, reviewer=request.user.reviewer)
                song.overall_rating = ((song.overall_rating * song.rating_count) \
                                       - rating_from_db.rate + float(new_rating)) / song.rating_count
                rating_from_db.rate = new_rating
                rating_from_db.save()
            except Rating.DoesNotExist:
                new_rating_obj = Rating(rate=new_rating, song=song, reviewer=request.user.reviewer)
                new_rating_obj.save()
                song.overall_rating = ((song.overall_rating * song.rating_count) \
                                       + float(new_rating)) / (song.rating_count + 1)
                song.rating_count += 1
            song.save()

    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    url = song.url
    url_data = urlparse(url)
    query = parse_qs(url_data.query)

    try:
        video_id = query["v"][0]
        params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails,statistics',
            'id': video_id
        }
        r = requests.get(video_url, params=params)
        results = r.json()['items'][0]
        song.thumbnail = results['snippet']['thumbnails']['high']['url']
        views = int(results['statistics']['viewCount'])
        song.views = f'{views:,}'
    except KeyError:
        song.thumbnail = None
        song.views = 'No information'

    user_rating = song.rating_set.filter(reviewer=request.user.reviewer)
    if not user_rating:
        song.user_rating = None
    else:
        song.user_rating = user_rating[0]
    context = {
        'song': song
    }
    return render(request, 'rate/song.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def ratedSongs(request):
    songs = Song.objects.filter(reviewers=request.user.reviewer)
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    for song in songs:
        url = song.url
        url_data = urlparse(url)
        query = parse_qs(url_data.query)
        try:
            video_id = query["v"][0]
            params = {
                'key': settings.YOUTUBE_DATA_API_KEY,
                'part': 'snippet,contentDetails,statistics',
                'id': video_id
            }
            r = requests.get(video_url, params=params)
            results = r.json()['items'][0]
            song.thumbnail = results['snippet']['thumbnails']['default']['url']
            views = int(results['statistics']['viewCount'])
            song.views = f'{views:,}'
        except KeyError:
            song.thumbnail = None
            song.url = ''
            song.views = '-'
        song.my_rating = song.rating_set.filter(reviewer=request.user.reviewer)[0]
    context = {
        'songs': songs
    }
    return render(request, 'rate/rated_songs.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def about(request):
    context = {
    }
    return render(request, 'rate/about.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            body = {
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, ['piotrsularz99@gmail.com'])
                messages.success(request, 'Message sent! Wait for my answer...')
            except:
                messages.success(request, 'Unable to send message. Try again later...')

    form = ContactForm(initial={'email': request.user.email})
    context = {
        'form': form
    }
    return render(request, 'rate/contact.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def profile(request):
    try:
        reviewer = request.user.reviewer
    except:
        return redirect('home')
    form = ReviewerForm(instance=reviewer)
    if request.method == 'POST':
        form = ReviewerForm(request.POST, instance=reviewer)
        if form.is_valid():
            form.save()
    context = {
        'form': form
    }
    return render(request, 'rate/profile.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def save(request, pk):
    context = {
    }
    return render(request, 'rate/rated_songs.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def searchToAdd(request):
    songs = []
    if request.method == 'POST':
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part': 'snippet',
            'q': request.POST['search'],
            'key': settings.YOUTUBE_DATA_API_KEY,
            'maxResults': 5,
            'type': 'video'
        }

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        song_ids = []
        for result in results:
            song_ids.append(result['id']['videoId'])

        song_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails,statistics',
            'id': ','.join(song_ids),
            'maxResults': 5
        }

        r = requests.get(video_url, params=song_params)

        results = r.json()['items']

        for result in results:
            video_data = {
                'id': result['id'],
                'title': result['snippet']['title'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'thumbnail': result['snippet']['thumbnails']['high']['url'],
                'views': result['statistics']['viewCount']
            }
            songs.append(video_data)
    context = {
        'songs': songs
    }
    return render(request, 'rate/search_to_add.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['reviewer', 'admin'])
def addSong(request, song_id):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            songs = Song.objects.all()
            appropriate_flag = True
            for song in songs:
                if form.cleaned_data.get('name').lower() == song.name.lower() or form.cleaned_data.get(
                        'url') == song.url:
                    messages.info(request, mark_safe('Can\'t add ' + form.cleaned_data.get('name') + \
                                                     "! Look <a href='/song/" + str(song.id) + "'>here</a>"))
                    appropriate_flag = False
                    break
            if appropriate_flag:
                form.save()
                messages.success(request, 'Song added! Now you can rate ' + form.cleaned_data.get('name'))

    song_url = f'https://www.youtube.com/watch?v={song_id}'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet,contentDetails,statistics',
        'id': song_id
    }
    r = requests.get(video_url, params=params)
    results = r.json()['items'][0]
    thumbnail = results['snippet']['thumbnails']['high']['url']
    title = results['snippet']['title']
    form = SongForm(initial={'url': song_url})
    context = {
        'form': form,
        'thumbnail': thumbnail,
        'title': title
    }
    return render(request, 'rate/add_song.html', context)
