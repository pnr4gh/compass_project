
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import re
from datetime import datetime
from .models import Accolade, AccoladeLike, Organization, Outcome, Scope
from .models import Accolade
from django.shortcuts import render
from .models import Accolade
@login_required
def accolade_list(request):
    username = request.GET.get('username', '').strip()
    
    if username:
        accolades = Accolade.objects.filter(posted_by__username__icontains=username).order_by('-post_datetime')
        user_not_found = not accolades.exists()  
    else:
        accolades = Accolade.objects.all().order_by('-post_datetime')
        user_not_found = False  

    context = {
        'accolades': accolades,
        'username': username,
        'user_not_found': user_not_found,
    }
    
    return render(request, 'decodeschool/accolade_list.html', context)


@login_required
def create_accolade(request):
    organizations = Organization.objects.all()
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            messages.error(request, 'Content is required.')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })

        org_match = re.search(r'Organization: (.*?)\n', content)
        org_name = org_match.group(1).strip() if org_match else None
        if not org_name:
            messages.error(request, 'Please include an organization name in the format "Organization: Name".')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })

        # Extract outcome details
        outcome_title_match = re.search(r'Outcome Title: (.*?)\n', content)
        outcome_score_match = re.search(r'Outcome Score: (.*?)\n', content)
        outcome_title = outcome_title_match.group(1).strip() if outcome_title_match else None
        outcome_score = outcome_score_match.group(1).strip() if outcome_score_match else None
        if not (outcome_title and outcome_score):
            messages.error(request, 'Please include outcome in the format "Outcome Title: Title\nOutcome Score: Value".')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })

        # Extract scope details
        scope_name_match = re.search(r'Scope: (.*?)\n', content)
        scope_score_match = re.search(r'Scope Score: (.*?)\n', content)
        scope_name = scope_name_match.group(1).strip() if scope_name_match else None
        scope_score = scope_score_match.group(1).strip() if scope_score_match else None
        if not (scope_name and scope_score):
            messages.error(request, 'Please include scope in the format "Scope: Name\nScope Score: Details".')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })

        # Extract skills (optional)
        skills_match = re.search(r'Skills: (.*?)\n', content)
        skills = skills_match.group(1).strip() if skills_match else ''

        # Extract date
        date_match = re.search(r'Date: (.*?)\n', content)
        date_str = date_match.group(1).strip() if date_match else None
        if not date_str:
            messages.error(request, 'Please include a date in the format "Date: YYYY-MM-DD".')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })

        try:
        
            accolade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            organization = Organization.objects.get(name=org_name)
            outcome, created = Outcome.objects.get_or_create(
                title=outcome_title,
                score=outcome_score
            )

            scope, created = Scope.objects.get_or_create(
                scope=scope_name,
                score=scope_score
            )
            cleaned_content = content
            if org_match:
                cleaned_content = re.sub(r'Organization:.*?\n', '', cleaned_content)
            if outcome_title_match:
                cleaned_content = re.sub(r'Outcome Title:.*?\n', '', cleaned_content)
            if outcome_score_match:
                cleaned_content = re.sub(r'Outcome Score:.*?\n', '', cleaned_content)
            if scope_name_match:
                cleaned_content = re.sub(r'Scope:.*?\n', '', cleaned_content)
            if scope_score_match:
                cleaned_content = re.sub(r'Scope Score:.*?\n', '', cleaned_content)
            if skills_match:
                cleaned_content = re.sub(r'Skills:.*?\n', '', cleaned_content)
            if date_match:
                cleaned_content = re.sub(r'Date:.*?\n', '', cleaned_content)

            cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
            accolade = Accolade.objects.create(
                content=cleaned_content,
                posted_by=request.user,
                organization=organization,
                outcome=outcome,
                scope=scope,
                skills=skills,
                date=accolade_date
            )

            messages.success(request, 'Accolade posted successfully!')
            return redirect('accolade_list')

        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })
        except Organization.DoesNotExist:
            messages.error(request, f'Organization "{org_name}" not found.')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })
        except Exception as e:
            messages.error(request, f'Error posting accolade: {str(e)}')
            return render(request, 'decodeschool/accolade_form.html', {
                'organizations': organizations,
                'username': request.user.username,
            })

    context = {
        'organizations': organizations,
        'username': request.user.username,
    }
    return render(request, 'decodeschool/accolade_form.html', context)

@login_required
def like_accolade(request, accolade_id):
    accolade = get_object_or_404(Accolade, id=accolade_id)
    like, created = AccoladeLike.objects.get_or_create(user=request.user, accolade=accolade)
    if not created:
        like.delete()
        liked_status = False
    else:
        liked_status = True
    return JsonResponse({'liked': liked_status, 'likes_count': accolade.likes.count()})

@login_required
def add_organization(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if name:
                org, created = Organization.objects.get_or_create(name=name)
                return JsonResponse({'id': org.id, 'name': org.name}, status=201)
            return JsonResponse({'error': 'Organization name is required'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def add_outcome(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            score = data.get('score')
            if title and score:
                outcome = Outcome.objects.create(title=title, score=score)
                return JsonResponse({'id': outcome.id, 'title': outcome.title, 'score': outcome.score}, status=201)
            return JsonResponse({'error': 'Both title and score are required'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def add_scope(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            scope = data.get('title')
            score = data.get('details')
            if scope and score:
                scope_obj = Scope.objects.create(scope=scope, score=score)
                return JsonResponse({'id': scope_obj.id, 'scope': scope_obj.scope, 'score': scope_obj.score}, status=201)
            return JsonResponse({'error': 'Both scope and score are required'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            file_path = default_storage.save(f"uploads/{image.name}", ContentFile(image.read()))
            image_url = default_storage.url(file_path)
            return JsonResponse({'url': image_url}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Failed to upload image: {str(e)}'}, status=400)
    return JsonResponse({'error': 'No image provided'}, status=400)