from track.models import Assignment, Assignment_Problems, Course, Course_Enrollement, Platform, Problem, ProblemTags, User_Handle, Solved_Problem, Profile, Batch, Institution, Department, Complexity,ProblemStats, Tags
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.db.models import Count, F, ExpressionWrapper, DecimalField, Q
from django.db import models
from django.core.paginator import Paginator


@login_required    
def leaderboard(request):
    user_tags = {}
    matching_problem_stats = []
    seen_user_problem_types = set()
    user_integrity_index = {}  # Will store average integrity_index per user

    solved_problems = Solved_Problem.objects.all()
    '''
    for solved_problem in solved_problems:
        user = solved_problem.user
        tags = solved_problem.get_tags()
        
        if user not in user_tags:
            user_tags[user] = set()
            user_integrity_index[user] = {'sum': 0, 'count': 0}  # Initialize sum and count
        
        user_tags[user].update(tags)

        problem_stats = ProblemStats.objects.filter(
            user=user,
            problem_type__name__in=tags,
        )

        for stat in problem_stats:
            problem_tags = ProblemTags.objects.filter(problem=solved_problem.problem)
            stat_tags = [tag.topictags.tag for tag in problem_tags]
            
            if set(tags).intersection(set(stat_tags)):
                user_problem_key = (user.id, stat.problem_type.name)
                
                if user_problem_key not in seen_user_problem_types:
                    seen_user_problem_types.add(user_problem_key)
                    matching_problem_stats.append(stat)
                    
                    # Sum the integrity_index values and increment count
                    user_integrity_index[user]['sum'] += getattr(stat, 'integrity_index', 0)
                    user_integrity_index[user]['count'] += 1

    # Calculate the average integrity_index for each user
    for user, data in user_integrity_index.items():
        average = data['sum'] / data['count'] if data['count'] > 0 else 0
        user_integrity_index[user] = average
        
        # Apply the logic to double the average if it is greater than 0.4
        if user_integrity_index[user] > 0.4:
            user_integrity_index[user] *= 
    '''
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
        department_id = request.GET.get('department')
        batch_id = request.GET.get('batch')
        institute_id = request.GET.get('institute')
        course_id = request.GET.get('course')
        platform_id = request.GET.get('platform')
        difficulty_id = request.GET.get('difficulty')
        page = int(request.GET.get('page', 1))  # Get the page number, default to 1

        queryset = Profile.objects.all()

        if department_id:
            queryset = queryset.filter(department__id=department_id)
        if batch_id:
            queryset = queryset.filter(batch__id=batch_id)
        if institute_id:
            queryset = queryset.filter(institute__id=institute_id)
        if course_id:
            queryset = queryset.filter(user__course_enrollement__course__id=course_id)
        
        if platform_id and difficulty_id:
            queryset = queryset.annotate(
                total_solved=Count(
                    'user__solved_problem',
                    filter=Q(
                        user__solved_problem__problem__platform__id=platform_id,
                        user__solved_problem__problem__complexity__id=difficulty_id
                    )
                ),
                easy_solved=Count(
                    'user__solved_problem',
                    filter=Q(
                        user__solved_problem__problem__complexity__level="Easy",
                        user__solved_problem__problem__platform__id=platform_id
                    )
                ),
                medium_solved=Count(
                    'user__solved_problem',
                    filter=Q(
                        user__solved_problem__problem__complexity__level="Medium",
                        user__solved_problem__problem__platform__id=platform_id
                    )
                ),
                hard_solved=Count(
                    'user__solved_problem',
                    filter=Q(
                        user__solved_problem__problem__complexity__level="Hard",
                        user__solved_problem__problem__platform__id=platform_id
                    )
                )
            ).annotate(total_score = ExpressionWrapper(F('total_solved') * F('integrity_index'), output_field=DecimalField()))
        elif platform_id:
            queryset = queryset.annotate(
                total_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__platform__id=platform_id)),
                easy_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Easy", user__solved_problem__problem__platform__id=platform_id)),
                medium_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Medium", user__solved_problem__problem__platform__id=platform_id)),
                hard_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Hard", user__solved_problem__problem__platform__id=platform_id))
            ).annotate(total_score = ExpressionWrapper(F('total_solved') * F('integrity_index'), output_field=DecimalField()))
        elif difficulty_id:
            queryset = queryset.annotate(
                total_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__id=difficulty_id)),
                easy_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Easy")),
                medium_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Medium")),
                hard_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Hard"))
            ).annotate(total_score = ExpressionWrapper(F('total_solved') * F('integrity_index'), output_field=DecimalField()))
        else:
            queryset = queryset.annotate(
                total_solved=Count('user__solved_problem'),
                easy_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Easy")),
                medium_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Medium")),
                hard_solved=Count('user__solved_problem', filter=Q(user__solved_problem__problem__complexity__level="Hard"))
            ).annotate(total_score = ExpressionWrapper(F('total_solved') * F('integrity_index'), output_field=DecimalField()))

        # Pagination logic
        paginator = Paginator(queryset.order_by('-total_score'), 20)  # 20 items per page
        page_obj = paginator.get_page(page)

        leaderboard_data = list(page_obj.object_list.values(
            'user__username', 'user__first_name', 'user__last_name',
            'department__short_name', 'batch__start_year', 'batch__end_year',
            'institute__name', 'easy_solved', 'medium_solved', 'hard_solved', 'total_score','total_solved','integrity_index'
        ))
        '''
        for entry in leaderboard_data :
            user = User.objects.get(username=entry['user__username'])
            entry['user_integrity_index'] = user_integrity_index.get(user, 0)
        '''
        response = {
            'data': leaderboard_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        }
        return JsonResponse(response, safe=False)
        

    context = {
        'departments': Department.objects.all(),
        'batches': Batch.objects.all(),
        'institutes': Institution.objects.all(),
        'courses': Course.objects.all(),
        'platforms': Platform.objects.all(),
        'difficulties': Complexity.objects.all(),
        #'user_integrity_index': user_integrity_index
        
    }
    return render(request, 'decodeschool/leaderboard.html', context)