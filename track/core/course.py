from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Count, Q, OuterRef, Subquery
from track.models import Course, Course_Enrollement, Assignment, Assignment_Problems, Solved_Problem, Institution, Profile, Batch, Tags as Tag, Problem, Complexity, Platform, ProblemTags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from track.forms import AssignmentForm
from django.core.paginator import Paginator
from django.db import models
from django.contrib.auth.models import User
from track.views import check_coordinator

@user_passes_test(check_coordinator)
def course_list_view(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'decodeschool/course.html', context)

@csrf_exempt
@require_POST
@user_passes_test(check_coordinator)
def create_course(request):
    course_title = request.POST.get('course_title')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    course = Course.objects.create(course_title=course_title, start_date=start_date, end_date=end_date, created_by=request.user)
    return JsonResponse({'id': course.id, 'course_title': course.course_title})

@csrf_exempt
@user_passes_test(check_coordinator)
def edit_course(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    if course.created_by == request.user:
        if request.method == 'GET':
            return JsonResponse({
                'id': course.id, 
                'course_title': course.course_title,
                'start_date': course.start_date,
                'end_date': course.end_date
            })
        elif request.method == 'POST':
            course.course_title = request.POST.get('course_title')
            course.start_date = request.POST.get('start_date')
            course.end_date = request.POST.get('end_date')
            course.save()
            return JsonResponse({'id': course.id, 'course_title': course.course_title})
    else:
        return HttpResponse("Not Eligible to do this")

# Course Detail View
@user_passes_test(check_coordinator)
def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    if course.created_by == request.user:

        assignments = Assignment.objects.filter(course=course).order_by('-id')
        
        # Adding additional data for the assignments
        for assignment in assignments:
            problems = assignment.assignment_problems_set.all()
            

        return render(request, 'decodeschool/course_detail.html', {
            'course': course,
            'assignments': assignments,
            'institutes': Institution.objects.all(),
        })
    else:
        return HttpResponse("Not Eligible to do this")

@user_passes_test(check_coordinator)
def student_progress(request,id):
    assignment = Assignment.objects.get(id=id)
    assignment_Problems = Assignment_Problems.objects.filter(assignment=assignment)
    profiles = Profile.objects.filter(user__course_enrollement__course=assignment.course)
    context={
        'assignment_problems':assignment_Problems,
        'profiles':profiles,
        'assignment_id':id,
        'assignment':assignment
    }
    return render(request,'decodeschool/assignment.html',context)

@csrf_exempt
@user_passes_test(check_coordinator)
def create_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'course_detail.html')

@csrf_exempt
@user_passes_test(check_coordinator)
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST' and assignment.course.created_by == request.user:
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@user_passes_test(check_coordinator)
def problem_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    tags = Tag.objects.all()
    platforms = Platform.objects.all()

    tags_filter = request.GET.get('tags', '')
    complexity_filter = request.GET.get('complexity', '')
    platform_filter = request.GET.get('platform', '')
    title_filter = request.GET.get('query')
    
    problems = Problem.objects.all()

    if tags_filter:
        problems = problems.filter(problemtags__topictags=tags_filter)

    if complexity_filter:
        problems = problems.filter(complexity__level=complexity_filter)

    if platform_filter:
        problems = problems.filter(platform__id=platform_filter)

    if title_filter:
         problems = problems.filter(problem_title__icontains=title_filter)

    offset = int(request.GET.get('offset', 0))
    problems = problems[offset:offset + 20]

    assigned_problems = Problem.objects.filter(assignment_problems__assignment=assignment)
    context = {
        'assignment': assignment,
        'problems': problems,
        'tags': tags,
        'platforms': platforms,
        'assigned_problems': assigned_problems, 
    }

    # For AJAX requests, return the partial HTML of the problem list
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
        return render(request, 'decodeschool/partial_problem_list.html', context)

    return render(request, 'decodeschool/problem_list.html', context)

@user_passes_test(check_coordinator)
def load_more_problems(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    offset = int(request.GET.get('offset', 0))
    problems = assignment.problems.all()[offset:offset + 20]
    context = {
        'problems': problems,
    }
    return render(request, 'decodeschool/partial_problem_list.html', context)

@csrf_exempt
@user_passes_test(check_coordinator)
def add_problem_to_assignment(request):
    assignment_id = request.POST.get('assignmentId')
    problem_id = request.POST.get('problemId')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    problem = get_object_or_404(Problem, id=problem_id)

    # Check if problem is already added
    if Assignment_Problems.objects.filter(assignment=assignment,problem=problem).exists():
        return JsonResponse({'message': 'Problem is already added'}, status=400)

    Assignment_Problems.objects.create(assignment=assignment,problem=problem)
    return JsonResponse({'message': 'Problem added successfully'}, status=200)

@csrf_exempt
@user_passes_test(check_coordinator)
def remove_problem_from_assignment(request):
    assignment_id = request.POST.get('assignmentId')
    problem_id = request.POST.get('problemId')
    assignment = get_object_or_404(Assignment, id=assignment_id)
    problem = get_object_or_404(Problem, id=problem_id)
    
    # Check if problem exists in the assignment
    if not Assignment_Problems.objects.filter(assignment=assignment,problem=problem).exists():
        return JsonResponse({'message': 'Problem is not assigned'}, status=400)

    Assignment_Problems.objects.filter(assignment=assignment,problem=problem).delete()
    return JsonResponse({'message': 'Problem removed successfully'}, status=200)
    
# Load Leaderboard View
def load_leaderboard(request, course_id):

    institute_id = request.GET.get('institute', 'all')
    assignment_id = request.GET.get('assignment', 'all')

    course = get_object_or_404(Course, id=course_id)
    queryset = Profile.objects.filter(user__course_enrollement__course=course)
    problems = Problem.objects.filter(assignment_problems__assignment__course=course)
      
    
    '''leaderboard_data = queryset.filter(user__solved_problem__problem__in=problems).annotate(
        solved_count=models.Sum('user__solved_problem')
    ).order_by('-user__solved_problem')'''

    if institute_id != 'all':
        leaderboard_data = User.objects.filter(
        solved_problem__problem__in=problems,course_enrollement__course=course,profile__institute_id=institute_id).annotate(
        total_solved=Count('solved_problem__problem', distinct=True)).order_by('-total_solved')
    else:
        leaderboard_data = User.objects.filter(
        solved_problem__problem__in=problems,course_enrollement__course=course).annotate(
        total_solved=Count('solved_problem__problem', distinct=True)).order_by('-total_solved')

    return render(request, 'decodeschool/leaderboard_content.html', {
        'leaderboard_data': leaderboard_data
    })




