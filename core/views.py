from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages

from .models import User, Cat, Comment, AdoptionRequests


def home(request):
    cats = Cat.objects.filter(is_available=True)
    return render(request, 'core/home.html', {
        'cats': cats
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, "core/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "core/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "core/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect('home')
    else:
        return render(request, "core/register.html")

@login_required
def add_cat(request):
    if request.method == "POST":
        name = request.POST["name"]
        age = request.POST["age"]
        address = request.POST["address"]
        phone = request.POST["phone"]
        description = request.POST["description"]
        image = request.POST["image"]
        temp_is_ill = request.POST.get('is_ill')
        owner = request.user
        is_ill = True if temp_is_ill == "True" else False
        illness = request.POST.get("illness", "") if is_ill else ""

        # Saving the Form Data
        Cat.objects.create(
            owner=owner,
            name=name,
            age=age,
            address=address,
            phone=phone,
            description=description,
            image=image,
            is_ill=is_ill,
            type_of_disease=illness
        )

        return redirect('home')
    return render(request, "core/add_cat.html")

@login_required
def profile(request):
    user_cats = Cat.objects.filter(owner=request.user)
    return render(request, "core/profile.html",{
        'cats': user_cats
    })

def cat_details(request, cat_id):
    cat = get_object_or_404(Cat, pk=cat_id, is_available=True)
    is_owner = (
            request.user.is_authenticated
            and request.user.username == cat.owner
    )
    user_has_requested = (
        request.user.is_authenticated
        and AdoptionRequests.objects.filter(cat=cat, user=request.user).exists()
    )
    if request.method == "POST":
        if 'comment' in request.POST:
            comment = request.POST['comment']
            comment = Comment(
                cat=cat,
                user=request.user,
                content=comment
            )
            comment.save()

        elif 'adoption_request' in request.POST and not cat.adoption_requests.filter(user=request.user).exists():
            AdoptionRequests.objects.create(
                cat=cat,
                user=request.user,
                request_date=timezone.now()
            )
            return redirect('cat_detail', cat_id=cat_id)

        elif 'cancel_adoption_request' in request.POST and cat.adoption_requests.filter(user=request.user).exists():
            cat.adoption_requests.filter(user=request.user).delete()
            return redirect('cat_detail', cat_id=cat_id)

        elif 'close_adoption' in request.POST and is_owner:
            cat.is_available = False
            cat.save()
            return redirect('home')

    request_list = AdoptionRequests.objects.filter(cat=cat)

    comments = Comment.objects.filter(cat=cat)
    return render(request, "core/cat_details.html", {
        'cat': cat,
        'cat_id': cat_id,
        'comments': comments,
        'user_has_requested': user_has_requested,
        'is_owner':is_owner,
        'request_list': request_list
    })

def approve_adoption(request, cat_id):
    cat = get_object_or_404(Cat, pk=cat_id, is_available=True)
    is_owner = (
        request.user.is_authenticated
        and request.user.username == cat.owner
    )
    if request.method == "POST" and is_owner:
        request_id = request.POST.get('request_id')
        adoption_request = get_object_or_404(AdoptionRequests, cat=cat, id=request_id)
        cat.is_adopted = True
        cat.save()

        adoption_request.status = 'Approved'
        adoption_request.save()
        messages.success(request, f"Adoption request by {adoption_request.user.username} approved.")
        return redirect('cat_detail', cat_id=cat_id)
    return render(request, 'core/cat_details.html', {
        'cat': cat,
        'request_list': cat.adoption_requests.all()
    })

