from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST,require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
import json
from django.core.exceptions import ValidationError
from django.db.models import Count


def company_list(request):
    # Fetch all companies ordered by name
    companies = Company.objects.all().order_by('name')
    
    # Get query parameters
    company_type = request.GET.get('company_type', '')
    search_query = request.GET.get('search', '')
    skill = request.GET.get('skill', '')
    salary_band = request.GET.get('salary_band', '')

    # Apply filters
    if company_type:
        companies = companies.filter(company_type=company_type)
    if search_query:
        companies = companies.filter(Q(name__icontains=search_query))
    if salary_band:
        companies = companies.filter(salary_bands__salary_range=salary_band)
    if skill:
        # Filter companies based on skills via related models
        companies = companies.filter(
            job_roles__interview_process__required_skills__skill_name__skill=skill
        ).distinct()

    # Fetch unique skills from the Skill model
    skills = Skill.objects.all()
    
    # Fetch unique salary bands from the SalaryBand model
    salary_bands = SalaryBand.objects.all()
    
    # Prepare context for rendering the template
    context = {
        'companies': companies,
        'company_type': company_type,
        'search_query': search_query,
        'skill': skill,  # Pass selected skill to template
        'salary_band': salary_band,  # Pass selected salary band to template
        'skills': skills,  # Pass all skills for dropdown
        'salary_bands': salary_bands,  # Pass all salary bands for dropdown
    }
    return render(request, 'decodeschool/company.html', context)




def add_company(request):
    if request.method == 'POST':
        name = request.POST.get('company_name')
        company_type = request.POST.get('company_type')
        
        if name and company_type:
            Company.objects.create(
                name=name,
                company_type=company_type
            )
            return redirect('company_list')
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def job_role_view(request, company_id=None):
    if company_id:
        company = get_object_or_404(Company, id=company_id)
        job_roles = JobRole.objects.filter(company=company)
    else:
        company = None
        job_roles = JobRole.objects.all()

    job_roles = job_roles.select_related('company').prefetch_related(
        Prefetch(
            'interview_process',
            queryset=InterviewProcess.objects.order_by('round_number')
        )
    )

    all_companies = Company.objects.all()
    company_filter = request.GET.get('company_filter') if not company else None
    company_type = request.GET.get('company_type') if not company else None
    salary_range = request.GET.get('salary_range')
    year = request.GET.get('year')
    search_query = request.GET.get('search')

    # Apply filters
    if company_filter:
        job_roles = job_roles.filter(company_id=company_filter)
    if company_type:
        job_roles = job_roles.filter(company__company_type=company_type)
    if salary_range:
        if salary_range == '20+':
            job_roles = job_roles.filter(package_in_LPA__gte=20)
        else:
            min_salary, max_salary = map(int, salary_range.split('-'))
            job_roles = job_roles.filter(
                package_in_LPA__gte=min_salary,
                package_in_LPA__lt=max_salary
            )
    if year:
        job_roles = job_roles.filter(year=year)
    if search_query:
        if company:
            job_roles = job_roles.filter(title__icontains=search_query)
        else:
            job_roles = job_roles.filter(
                Q(title__icontains=search_query) |
                Q(company__name__icontains=search_query)
            )

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(job_roles, 10)
    try:
        job_roles = paginator.page(page)
    except PageNotAnInteger:
        job_roles = paginator.page(1)
    except EmptyPage:
        job_roles = paginator.page(paginator.num_pages)

    page_range = range(
        max(1, job_roles.number - 2),
        min(job_roles.paginator.num_pages + 1, job_roles.number + 3)
    )

    context = {
        'company': company,
        'job_roles': job_roles,
        'all_companies': all_companies,
        'company_filter': company_filter,
        'company_type': company_type,
        'salary_range': salary_range,
        'year': year,
        'search_query': search_query,
        'page_range': page_range,
        'years': range(2020, 2026),
    }
    return render(request, 'decodeschool/job_role.html', context)

@require_POST
def update_company(request):
    data = json.loads(request.body)
    company = get_object_or_404(Company, id=data.get('company_id'))
    if 'company_name' in data:
        company.name = data['company_name']
    if 'company_type' in data:
        company.company_type = data['company_type']
    company.save()
    return JsonResponse({
        'status': 'success',
        'message': 'Company updated successfully'
    })

@require_http_methods(["POST"])
def add_job_role(request):
    try:
        data = json.loads(request.body)
        
        company = get_object_or_404(Company, id=data.get('company'))
        
        required_fields = ['title', 'package_in_LPA', 'job_description', 'hiring_process', 'year']
        for field in required_fields:   
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field.replace("_", " ").title()} is required'
                }, status=400)
        
        try:
            package = float(data['package_in_LPA'])
            year = int(data['year'])
            
            if package <= 0:
                raise ValueError("Package must be greater than 0")
            if year < 1900 or year > 2100: 
                raise ValueError("Invalid year")
                
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
        job_role = JobRole.objects.create(
            company=company,
            title=data['title'],
            package_in_LPA=package,
            job_description=data['job_description'],
            hiring_process=data['hiring_process'],
            year=year
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Job role created successfully',
            'job_role_id': job_role.id,
            'job_role_title': job_role.title
        })
        
    except ValidationError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)
        
@require_http_methods(["GET"])
def interview_rounds(request, job_role_id):
    job_role = get_object_or_404(JobRole, id=job_role_id)
    interview_process = job_role.interview_process.all().order_by('round_number')
    
    context = {
        'job_role': job_role,
        'interview_process': interview_process,
    }
    
    return render(request, 'decodeschool/rounds.html', context)

@require_http_methods(["POST"])
def add_interview_round(request):
    """View to add a new interview round"""
    if request.method == 'POST':
        job_role_id = request.POST.get('job_role_id')
        round_name = request.POST.get('round_name')
        round_type = request.POST.get('round_type')
        description = request.POST.get('description', '')
        
        try:
            job_role = JobRole.objects.get(id=job_role_id)
            
         
            latest_round = InterviewProcess.objects.filter(job_role=job_role).order_by('-round_number').first()
            round_number = 1 if not latest_round else latest_round.round_number + 1
            
           
            new_round = InterviewProcess.objects.create(
                job_role=job_role,
                round_name=round_name,
                round_number=round_number,
                round_type=round_type,
                description=description
            )
            
            return JsonResponse({
                'status': 'success',
                'round_id': new_round.id,
                'round_number': new_round.round_number,
                'round_name': new_round.round_name,
                'round_type': new_round.get_round_type_display(),
                'description': new_round.description
            })
        except JobRole.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Job role not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_http_methods(["POST"])
def add_skill_to_round(request):
    """View to add a skill to an interview round"""
    if request.method == 'POST':
        round_id = request.POST.get('round_id')
        skill_name = request.POST.get('skill_name')
        
        if round_id and skill_name:
            try:
                interview_round = InterviewProcess.objects.get(id=round_id)
                
                skill, created = Skill.objects.get_or_create(skill=skill_name)
                
               
                round_skill = Round_Skills.objects.create(
                    interview_round=interview_round,
                    skill_name=skill
                )
                
                return JsonResponse({
                    'status': 'success',
                    'round_skill_id': round_skill.id,
                    'skill_name': skill.skill
                })
            except InterviewProcess.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Interview round not found'})
        return JsonResponse({'status': 'error', 'message': 'Round ID and skill name are required'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_http_methods(["POST"])
def remove_skill_from_round(request):
    """View to remove a skill from an interview round"""
    if request.method == 'POST':
        round_skill_id = request.POST.get('round_skill_id')
        
        if round_skill_id:
            try:
                round_skill = Round_Skills.objects.get(id=round_skill_id)
                round_skill.delete()
                return JsonResponse({'status': 'success'})
            except Round_Skills.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Skill relation not found'})
        return JsonResponse({'status': 'error', 'message': 'Round skill ID is required'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



@require_http_methods(["GET"])
def get_topics_for_skill(request, round_skill_id):
    """View to get all topics for a skill"""
    try:
        round_skill = Round_Skills.objects.get(id=round_skill_id)
        topics = Round_Skill_Detail.objects.filter(round_skill=round_skill)
        
        topics_data = [
            {
                'id': topic.id,
                'tag_name': topic.tags.tag,  
                'weight': topic.weight
            }
            for topic in topics
        ]
        
        return JsonResponse({
            'status': 'success',
            'topics': topics_data
        })
    except Round_Skills.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Skill not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_http_methods(["POST"])
def add_topic_to_skill(request):
    """View to add a topic to a skill"""
    if request.method == 'POST':
        round_skill_id = request.POST.get('round_skill_id')
        topic_name = request.POST.get('topic_name')
        weight = request.POST.get('weight')
        
        if not all([round_skill_id, topic_name, weight]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
        
        try:
            round_skill = Round_Skills.objects.get(id=round_skill_id)
            
            tag, created = Tags.objects.get_or_create(tag=topic_name)  
            
            topic = Round_Skill_Detail.objects.create(
                round_skill=round_skill,
                tags=tag,
                weight=weight
            )
            
            return JsonResponse({
                'status': 'success',
                'topic_id': topic.id,
                'tag_name': tag.tag,  
                'weight': topic.weight
            })
        except Round_Skills.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Skill not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_http_methods(["POST"])
def remove_topic_from_skill(request):
    """View to remove a topic from a skill"""
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        
        if not topic_id:
            return JsonResponse({'status': 'error', 'message': 'Topic ID is required'})
        
        try:
            topic = Round_Skill_Detail.objects.get(id=topic_id)
            topic.delete()
            
            return JsonResponse({'status': 'success'})
        except Round_Skill_Detail.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Topic not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_http_methods(["POST"])
def save_topics(request):
    """View to save all topics for a skill"""
    if request.method == 'POST':
        data = json.loads(request.body)
        round_skill_id = data.get('round_skill_id')
        
        if not round_skill_id:
            return JsonResponse({'status': 'error', 'message': 'Round skill ID is required'})
        
        try:
            # Just return success - all changes are already saved in the database
            # This endpoint is just for confirmation purposes
            return JsonResponse({'status': 'success', 'message': 'Topics saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



@require_http_methods(["GET"])
def get_all_topics(request):
    """View to get all topics for autocomplete"""
    try:
        # Get all tags from the database
        tags = Tags.objects.all().order_by('tag')
        
        # Convert to list of dictionaries
        tags_data = [
            {
                'id': tag.id,
                'tag_name': tag.tag
            }
            for tag in tags
        ]
        
        return JsonResponse({
            'status': 'success',
            'topics': tags_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@require_http_methods(["GET"])
def get_all_skills(request):
    """View to get all skills for autocomplete"""
    try:
        skills = Skill.objects.all().order_by('skill')
        skills_data = [
            {
                'id': skill.id,
                'skill_name': skill.skill
            }
            for skill in skills
        ]
        return JsonResponse({
            'status': 'success',
            'skills': skills_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



def company_dashboard(request):
    # Get counts of product-based and service-based companies
    company_counts = Company.objects.values('company_type').annotate(count=Count('id'))
    product_count = 0
    service_count = 0
    total_companies = 0

    for entry in company_counts:
        if entry['company_type'] == 'PRODUCT':
            product_count = entry['count']
        elif entry['company_type'] == 'SERVICE':
            service_count = entry['count']
        total_companies += entry['count']

    # Get year-wise counts of product and service-based companies
    year_wise_counts = (
        Company.objects.values('created_at__year', 'company_type')
        .annotate(count=Count('id'))
        .order_by('created_at__year')
    )

    # Organize year-wise data for the bar chart
    years = sorted(set(entry['created_at__year'] for entry in year_wise_counts))
    product_data = []
    service_data = []

    for year in years:
        product_data.append(
            next(
                (entry['count'] for entry in year_wise_counts if entry['created_at__year'] == year and entry['company_type'] == 'PRODUCT'),
                0,
            )
        )
        service_data.append(
            next(
                (entry['count'] for entry in year_wise_counts if entry['created_at__year'] == year and entry['company_type'] == 'SERVICE'),
                0,
            )
        )

    context = {
        'product_count': product_count,
        'service_count': service_count,
        'total_companies': total_companies,
        'years': years,
        'product_data': product_data,
        'service_data': service_data,
    }

    return render(request, 'decodeschool/company_dashboard.html', context)


def skill_company_data(request):
    # Aggregate skills and their associated company counts
    skill_data = (
        Round_Skills.objects.values('skill_name__skill')
        .annotate(company_count=Count('interview_round__job_role__company', distinct=True))
        .order_by('-company_count')
    )

    # Format the data for JSON response
    data = [
        {
            'skill': entry['skill_name__skill'],
            'company_count': entry['company_count']
        }
        for entry in skill_data
    ]

    return JsonResponse(data, safe=False)


def salary_band_data(request):
    # Aggregate salary bands and their associated company counts
    salary_band_data = (
        SalaryBand.objects.values('salary_range')
        .annotate(company_count=Count('companies', distinct=True))
        .order_by('salary_range')
    )

    # Format the data for JSON response
    data = [
        {
            'salary_band': entry['salary_range'],
            'company_count': entry['company_count']
        }
        for entry in salary_band_data
    ]

    return JsonResponse(data, safe=False)