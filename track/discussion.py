from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction

@login_required
def discussion_detail_view(request, course_id, discussion_id):
    course = get_object_or_404(Course, id=course_id)
    discussion = get_object_or_404(Discussion, id=discussion_id, course=course)
    
    if discussion_detail.objects.filter(discussion=discussion).exists():
        return redirect('discussion_results', course_id=course_id, discussion_id=discussion_id)
    
    if request.method == "POST":
        users_list = request.POST.getlist('users[]')
        problems_list = request.POST.getlist('problems[]')
        integrity_scores = request.POST.getlist('integrity_scores[]')
        communication_scores = request.POST.getlist('communication_scores[]')
        comments_list = request.POST.getlist('comments[]')

        if not (users_list and problems_list and integrity_scores and communication_scores and comments_list):
            return JsonResponse({'success': False, 'error': "All fields must be filled."})

        try:
            with transaction.atomic():
                users_dict = {user.id: user for user in User.objects.filter(id__in=users_list)}
                problems_dict = {problem.id: problem for problem in Problem.objects.filter(id__in=problems_list)}

                discussion_details_to_create = []
                user_profile_updates = {}

                for i, (user_id, problem_id, integrity_score, communication_score, comment) in enumerate(
                    zip(users_list, problems_list, integrity_scores, communication_scores, comments_list)
                ):
                    user_id = int(user_id)
                    problem_id = int(problem_id)
                    integrity_score = int(integrity_score)

                    discussion_details_to_create.append(discussion_detail(
                        discussion=discussion,
                        user=users_dict[user_id],
                        problem=problems_dict[problem_id],
                        integrity_score=integrity_score,
                        communication_score=communication_score,
                        comments=comment
                    ))

                    if user_id not in user_profile_updates:
                        user_profile_updates[user_id] = {
                            'integrity_score_sum': integrity_score,
                            'discussion_count': 1
                        }
                    else:
                        user_profile_updates[user_id]['integrity_score_sum'] += integrity_score
                        user_profile_updates[user_id]['discussion_count'] += 1

                discussion_detail.objects.bulk_create(discussion_details_to_create)

                profiles_dict = {profile.user_id: profile for profile in Profile.objects.filter(user_id__in=user_profile_updates.keys())}

                for user_id, updates in user_profile_updates.items():
                    profile = profiles_dict.get(user_id)
                    if profile:
                        profile.discussion_score += updates['integrity_score_sum']
                        profile.no_of_discussion += updates['discussion_count']
                        profile.discussion_index = profile.discussion_score / profile.no_of_discussion if profile.no_of_discussion else 0
                        profile.integrity_index = profile.discussion_index 

                Profile.objects.bulk_update(profiles_dict.values(), ['discussion_score', 'no_of_discussion', 'discussion_index', 'integrity_index'])

                return JsonResponse({
                    'success': True, 
                    'redirect_url': f'/discussion_results/{course_id}/{discussion_id}/'
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    users = User.objects.filter(course_enrollement__course_id=course_id).only('id', 'username').distinct()
    integrity_choices = discussion_detail.INTEGRITY_CHOICES
    communication_choices = discussion_detail.COMMUNICATION_CHOICES

    return render(request, 'decodeschool/course_discussion.html', {
        'users': users,
        'integrity_choices': integrity_choices,
        'communication_choices': communication_choices,
        'course': course,
        'discussion': discussion,
        'course_id': course_id,
        'discussion_id': discussion_id,
    })
@login_required
def discussion_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    discussions = Discussion.objects.filter(course=course).order_by("id")

    return render(request, 'decodeschool/course_detail.html', {
        'course': course,
        'discussions': discussions,
    })

@login_required
def discussion_results(request, course_id, discussion_id):
    course = get_object_or_404(Course, id=course_id)
    discussion = get_object_or_404(Discussion, id=discussion_id, course=course)
    discussion_details = discussion_detail.objects.select_related('user', 'problem').filter(discussion=discussion).order_by("-date")

    return render(request, 'decodeschool/discussion_results.html', {
        'course': course,
        'discussion': discussion,
        'discussion_details': discussion_details,
    })

@login_required
def get_solved_problems(request, user_id):
    course_id = request.GET.get('course_id')
    user = get_object_or_404(User, id=user_id)

    course_problems = Problem.objects.filter(
        assignment_problems__assignment__course_id=course_id
    ).distinct()
    
    solved_problems = Problem.objects.filter(
        solved_problem__user=user,
        assignment_problems__assignment__course_id=course_id
    ).distinct()
    
    problems = [{'id': p.id, 'title': p.problem_title} for p in solved_problems]
    
    return JsonResponse({
        'problems': problems,
        'total_course_problems': course_problems.count(),
        'solved_count': solved_problems.count()
    })


@login_required
def add_or_show_discussion(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'GET':
        discussions = Discussion.objects.filter(course=course).order_by('id')
        discussions_data = [
            {'id': discussion.id, 'discussion_name': discussion.discussion_name}
            for discussion in discussions
        ]
        return JsonResponse({'discussions': discussions_data})

    elif request.method == 'POST':
        if not request.user.is_superuser and request.user != course.created_by:
            return JsonResponse({'success': False, 'error': 'You do not have permission to create a discussion.'}, status=403)

        discussion_count = Discussion.objects.filter(course=course).count()
        discussion_name = f"Discussion {discussion_count + 1}"
        
        discussion = Discussion.objects.create(
            discussion_name=discussion_name,
            course=course
        )

        return JsonResponse({
            'success': True,
            'discussion_name': discussion.discussion_name,
            'discussion_id': discussion.id
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


