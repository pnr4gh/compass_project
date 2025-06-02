from django.shortcuts import render, redirect
from .models import Quiz, Skill, Tags
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import QuizForm  
from django.db.models import Case, When, IntegerField
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quiz
from .forms import QuizForm,QuestionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Attempt
from .forms import QuizForm
from datetime import datetime
from django.forms import modelformset_factory
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuizForm
from .models import Attempt, Quiz, Question
import json
import random
from .models import Attempt, Response, User_Score
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Response, Question, Option, Attempt
from reportlab.lib.colors import green
from django.http import JsonResponse
import re
import math
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Attempt, Response, Option


@login_required
def aura_page(request):
    
        user = request.user
        current_date = datetime.now().date()
        skills = Skill.objects.all()
        # Clearing session data
        request.session.pop('shuffled_questions', None)
        request.session.pop('attempt_id', None)

        try:
            user_attempts = Attempt.objects.filter(user=request.user)
        except Exception:
            messages.error(request, "Error fetching user attempts.")
            user_attempts = []

        try:
            
            attempt_count = Attempt.objects.filter(user=user).count()
        except Exception:
            messages.error(request, "Error fetching quiz or attempts count.")
            attempt_count = 0
            current_time = datetime.now()
            expired_quizzes = Quiz.objects.filter(closeDate__lt=current_time, isActive=True)
            expired_quizzes.update(isActive=False)
        
        
        all_selected_questions = 0
        if request.method == "POST":
           
            form = QuizForm(request.POST)
            

            if form.is_valid():
                try:
                    no_of_questions = form.cleaned_data.get('noOfQuestions')
                    skill = form.cleaned_data.get('skill')
                    tags = form.cleaned_data.get('tags')
                    practice = form.cleaned_data.get('is_practice')
                except Exception:
                    messages.error(request, "Error retrieving form data.")
                    return redirect("aura_page")

                try:
                    if practice:
                        analytical_count = (no_of_questions * 0.50)
                        conceptual_count =math.ceil (no_of_questions * 0.30)
                        memory_count = (no_of_questions * 0.20)  

                        analytical_questions = (Question.objects.filter(camp_category='A', skill=skill, is_practice=practice, tags__in=tags.all())[:analytical_count]).count()
                        conceptual_questions = (Question.objects.filter(camp_category='C', skill=skill, is_practice=practice, tags__in=tags.all())[:conceptual_count]).count()
                        memory_questions = (Question.objects.filter(camp_category='M', skill=skill, is_practice=practice, tags__in=tags.all())[:memory_count]).count()

                        all_selected_questions = analytical_questions + conceptual_questions + memory_questions
                    else:
                        practice_questions = Question.objects.filter(is_practice=True, skill=skill, tags__in=tags.all()).count()
                        non_practice_questions = Question.objects.filter(is_practice=False, skill=skill, tags__in=tags.all()).count()
                        practice_question_count = int(practice_questions * 0.60)
                        non_practice_question_count = int(non_practice_questions * 0.40)

                        all_selected_questions = practice_question_count + non_practice_question_count
                except Exception:
                    messages.error(request, "Error selecting questions.")
                    return redirect("aura_page")

                if all_selected_questions < no_of_questions:
                    remaining_questions = no_of_questions - all_selected_questions
                    analytical_questions = (Question.objects.filter(camp_category='A', skill=skill, is_practice=practice, tags__in=tags.all()).count())
                    remaining_analytical = int(abs(analytical_questions-analytical_questions))
                    if remaining_analytical < remaining_questions:
                        messages.error(request, "Not enough questions available in the specified categories.")
                        form = QuizForm(request.POST)
                    
                        quizzes = Quiz.objects.all().order_by('openDate')
                        
                        return render(request, "decodeschool/aura.html", {
                            "form": form, "quizzes": quizzes, "attempt_count": attempt_count,
                            "current_date": current_date,"all_selected_questions": all_selected_questions, "user_attempts": user_attempts, "skills": skills, "tags": tags
                        })

                if request.user.is_staff or request.user.is_superuser:
                    try:
                        form.save()
                        messages.success(request, "Quiz created successfully!")
                        return redirect("aura_page")
                    except Exception:
                        messages.error(request, "Error saving quiz.")

        try:
            quizzes = (Quiz.objects.all().order_by('-isActive', 'openDate') if request.user.is_staff or request.user.is_superuser
                    else Quiz.objects.filter(isActive=True).order_by('openDate'))
        except Exception:# check 
            quizzes = []


        form = QuizForm()

        skills = Skill.objects.all()
        tags = Tags.objects.all()

        return render(request, "decodeschool/aura.html", {
            "form": form,
            "quizzes": quizzes,
            "attempt_count": attempt_count,
            "current_date": current_date,
            "user_attempts": user_attempts,
            "skills": skills,
            "tags": tags,
            
            
        })



@login_required
def update_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            open_date = request.POST.get('openDate')
            close_date = request.POST.get('closeDate')
            max_marks = request.POST.get('maxMarks')
            no_of_attempts = request.POST.get('noOfAttempts')
            skill_id = request.POST.get('skill')
            is_practice = request.POST.get('is_practice') == 'on'
            
            # Validate required fields
            if not all([name, open_date, close_date, max_marks, no_of_attempts, skill_id]):
                messages.error(request, "All fields are required.")
                return redirect("aura_page")
            
            # Convert integer fields safely
            
            no_of_questions = int(request.POST.get('noOfQuestions', 0))
            max_marks = (max_marks)# check for integer
            no_of_attempts = int(no_of_attempts)
            
            # Ensure valid dates
            
            open_date = datetime.strptime(open_date, "%Y-%m-%d").date()
            close_date = datetime.strptime(close_date, "%Y-%m-%d").date()
            

            # Ensure close_date is after open_date
            if close_date < open_date:
                messages.error(request, "Close date must be after open date.")
                return redirect("aura_page")

            # Fetch the skill object safely
            skill = get_object_or_404(Skill, id=skill_id)

            # Update quiz fields
            quiz.name = name
            quiz.openDate = open_date
            quiz.closeDate = close_date
            quiz.maxMarks = max_marks
            quiz.noOfAttempts = no_of_attempts
            quiz.noOfQuestions = no_of_questions
            quiz.skill = skill
            quiz.is_practice = is_practice

            # Handle tags selection
            if 'tags' in request.POST:
                try:
                    tag_ids = request.POST.getlist('tags')
                    tags = Tags.objects.filter(id__in=tag_ids)
                    quiz.tags.set(tags)
                except Exception as e:
                    messages.error(request, f"Error selecting tags: {str(e)}")
                    return redirect("aura_page")

            # Determine the number of questions available
            if is_practice:
                analytical_count = (no_of_questions * 0.50)
                conceptual_count = math.ceil(no_of_questions * 0.30)
                memory_count = (no_of_questions * 0.20)

                analytical_questions = (Question.objects.filter(camp_category='A', skill=quiz.skill, is_practice=True, tags__in=quiz.tags.all())[:analytical_count]).count()
                conceptual_questions =( Question.objects.filter(camp_category='C', skill=quiz.skill, is_practice=True, tags__in=quiz.tags.all())[:conceptual_count]).count()
                memory_questions = (Question.objects.filter(camp_category='M', skill=quiz.skill, is_practice=True, tags__in=quiz.tags.all())[:memory_count]).count()
                all_selected_questions = analytical_questions + conceptual_questions +memory_questions
            
            else:
                practice_questions = Question.objects.filter(
                    is_practice=True, skill=quiz.skill, tags__in=quiz.tags.all()
                ).count()
                non_practice_questions = Question.objects.filter(
                    is_practice=False, skill=quiz.skill, tags__in=quiz.tags.all()
                ).count()

                practice_question_count = int(practice_questions * 0.60)
                non_practice_question_count = int(non_practice_questions * 0.40)
                all_selected_questions = practice_question_count + non_practice_question_count

            # Validate question availability
            if all_selected_questions < no_of_questions:
                remaining_questions = no_of_questions - all_selected_questions
                print("remaining_questions need",remaining_questions)
                total_analytical = (Question.objects.filter(camp_category='A', skill=quiz.skill, is_practice=True, tags__in=quiz.tags.all())).count()
                print("total_analytical",total_analytical)
                remaining_analytical = int(abs(total_analytical-analytical_questions))
                print("remaining_analytical",remaining_analytical)
                if remaining_analytical < remaining_questions:
                    messages.error(request, "Not enough questions available in the specified categories.")
                    return redirect("aura_page")
                
            quiz.save()
            messages.success(request, f"Quiz '{name}' updated successfully.")
            return redirect('aura_page')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("aura_page")

    return redirect('aura_page')





@login_required
def take_quiz(request, quiz_id):
    

    quiz = get_object_or_404(Quiz, id=quiz_id)
    

    user = request.user

    try:
        if 'shuffled_questions' in request.session and 'attempt_id' in request.session:
            shuffled_question_ids = json.loads(request.session.get('shuffled_questions', '[]'))
            order_conditions = [When(id=id, then=index) for index, id in enumerate(shuffled_question_ids)]

            selected_questions = Question.objects.filter(id__in=shuffled_question_ids).annotate(
                order=Case(*order_conditions, default=999999, output_field=IntegerField())
            ).order_by('order')

            attempt_id = request.session.get('attempt_id')

            attempt = get_object_or_404(Attempt, id=attempt_id, user=user, quiz=quiz)
        else:
            if not quiz.is_practice:
                try:
                    practice_quizzes = Quiz.objects.filter(
                        is_practice=True,openDate__lte=datetime.now(), closeDate__gte=datetime.now()
                    )

                    # Get the distinct completed practice attempts
                    completed_practice_attempts = Attempt.objects.filter(
                        user=user, quiz__in=practice_quizzes
                    ).values_list('quiz', flat=True).distinct()

                    # Check if all practice quizzes have been completed
                    if set(completed_practice_attempts) != set(practice_quizzes.values_list('id', flat=True)):
                        messages.error(request, "Complete all practice quizzes first.")
                        return redirect('aura_page')
                    

                    failed_practice_quizzes = practice_quizzes.exclude(
                        id__in=Attempt.objects.filter(user=user, score__gte=50).values_list('quiz', flat=True)
                    )
                    if failed_practice_quizzes.exists():
                        messages.error(request, "You scored less than 50% in some practice quizzes.")
                        return redirect('aura_page')
                except Exception as e:
                    messages.error(request, "Error fetching practice quiz attempts.")
                    return redirect('aura_page')

            user_attempts = Attempt.objects.filter(user=user, quiz=quiz).count()
            if user_attempts >= quiz.noOfAttempts:
                messages.error(request, 'You have reached the maximum number of attempts for this Test.')
                return redirect('aura_page')

            total_questions = quiz.noOfQuestions
            selected_questions = []

            try:
                if quiz.is_practice:
                    analytical_count = int(total_questions * 0.50)  # 50% of total questions
                    conceptual_count = math.ceil(total_questions * 0.30)  # 30% of total questions
                    memory_count = int(total_questions * 0.20)  # 20% of total questions

                    # Fetch analytical questions
                    analytical_questions = list(Question.objects.filter(
                        camp_category='A', 
                        skill=quiz.skill, 
                        is_practice=True, 
                        tags__in=quiz.tags.all()
                    ).distinct().order_by('?')[:analytical_count])

                    # Fetch conceptual and memory questions
                    conceptual_questions = list(Question.objects.filter(
                        camp_category='C', 
                        skill=quiz.skill, 
                        is_practice=True, 
                        tags__in=quiz.tags.all()
                    )[:conceptual_count])

                    memory_questions = list(Question.objects.filter(
                        camp_category='M', 
                        skill=quiz.skill, 
                        is_practice=True, 
                        tags__in=quiz.tags.all()
                    )[:memory_count])

                    # Combine the questions
                    selected_questions = analytical_questions + conceptual_questions + memory_questions
                    print("selected_questions (after initial fetch):", len(selected_questions))

                else:
                    practice_question_count = int(total_questions * 0.60)  # 60% for practice
                    non_practice_question_count = int(total_questions * 0.40)  # 40% for non-practice

                    # Fetch practice and non-practice questions
                    practice_questions = list(Question.objects.filter(
                        skill=quiz.skill, 
                        is_practice=True, 
                        tags__in=quiz.tags.all()
                    ).distinct().order_by('?')[:practice_question_count])

                    non_practice_questions = list(Question.objects.filter(
                        skill=quiz.skill, 
                        is_practice=False, 
                        tags__in=quiz.tags.all()
                    ).distinct().order_by('?')[:non_practice_question_count])

                    # Combine practice and non-practice questions
                    selected_questions = practice_questions + non_practice_questions

                # If we don't have enough questions, fetch additional analytical questions without overlap
                if len(selected_questions) < total_questions:
                    pending_analytical = total_questions - len(selected_questions)
                    print("pending_analytical", pending_analytical)

                    # Ensure no overlap with previously selected analytical questions by excluding those already selected
                    analytical_questions_remaining = list(Question.objects.filter(
                        camp_category='A', 
                        skill=quiz.skill, 
                        is_practice=True, 
                        tags__in=quiz.tags.all()
                    ).exclude(id__in=[q.id for q in selected_questions]).distinct().order_by('?')[:pending_analytical])

                    print("analytical_questions_remaining", len(analytical_questions_remaining))

                    # Add the additional analytical questions to the selection
                    selected_questions += analytical_questions_remaining

                # Print the final number of selected questions
                print("1 selected_questions (final count)", len(selected_questions))


                try:
                    # Ensure shuffling happens only once and selected_questions is not altered further.
                    if 'shuffled_questions' not in request.session:
                        random.shuffle(selected_questions)

                    attempt = Attempt.objects.create(user=request.user, quiz=quiz, attemptNo=user_attempts + 1)

                    # Save the shuffled question IDs to the session
                    request.session['shuffled_questions'] = json.dumps([q.id for q in selected_questions])
                    request.session['attempt_id'] = attempt.id

                    shuffled_question_ids = json.loads(request.session['shuffled_questions'])

                    # Print the shuffled question IDs before removing duplicates to check what they look like
                    print("Shuffled question IDs (before deduplication):", shuffled_question_ids)

                    # Remove duplicates and ensure the IDs are unique
                    shuffled_question_ids = list(dict.fromkeys(shuffled_question_ids))  # This preserves order and removes duplicates
                    
                    # Print the shuffled question IDs after removing duplicates
                    print("Shuffled question IDs (unique):", shuffled_question_ids)

                    # Ensure that we now have the correct number of unique IDs
                    print("Number of unique shuffled question IDs:", len(shuffled_question_ids))

                    order_conditions = [When(id=id, then=index) for index, id in enumerate(shuffled_question_ids)]

                    # Retrieve the questions using the shuffled IDs
                    selected_questions = Question.objects.filter(id__in=shuffled_question_ids).annotate(
                        order=Case(*order_conditions, default=999999, output_field=IntegerField())
                    ).order_by('order')

                    print("2 selected_questions", len(selected_questions))

                except Exception as e:
                    messages.error(request, "Error fetching quiz questions.")
                    return redirect('aura_page')



            except Exception as e:
                messages.error(request, "Error creating attempt or shuffling questions.")
                return redirect('aura_page')

    except Exception as e:
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('aura_page')

    context = {
        'quiz': quiz,
        'questions': selected_questions,
        'attempt': attempt
    }

    return render(request, 'decodeschool/take_quiz.html', context)


@login_required
def submit_quiz(request, quiz_id, attempt_id):
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user, quiz=quiz)
    
    if request.method == 'POST':
       
        score = 0
        questions = Question.objects.filter(skill=quiz.skill, tags__in=quiz.tags.all())
      

        try:
                for question in questions:
                    selected_option_id = request.POST.get(f'question_{question.id}')
                    if selected_option_id:
                        try:
                            selected_option = Option.objects.get(id=selected_option_id)
                        except Option.DoesNotExist:
                            messages.error(request, f"Selected option does not exist for question {question.id}")
                            continue
                        except Exception as e:
                            messages.error(request, f"Error fetching selected option: {e}")
                            continue

                        if selected_option.value == 1:  
                            score += 1  

                        try:
                            Response.objects.create(
                                user=request.user,
                                Option=selected_option,
                                Question=question,
                                Attempt=attempt
                            )
                        except Exception as e:
                            messages.error(request, f"Error saving response for question {question.id}: {e}")

                try:
                    user_score = User_Score.objects.create(user=request.user, user_score=str(int(score)), quiz=quiz)
                except Exception as e:
                    messages.error(request, f"Error saving user score: {e}")

                try:
                    attempt.score = int(score)
                    attempt.save()
                except Exception as e:
                    messages.error(request, f"Error saving attempt score: {e}")

        except Exception as e:
            messages.error(request, f"Unexpected error while processing the quiz: {e}")
            return redirect("aura_page")

    
        if 'shuffled_questions' in request.session:
            del request.session['shuffled_questions']
        if 'attempt_id' in request.session:
            del request.session['attempt_id']
        

        return redirect('quiz_result', quiz_id=quiz.id, attempt_id=attempt.id)





@login_required
def quiz_result(request, quiz_id, attempt_id):
    
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user, quiz=quiz_id)
    

    quiz = attempt.quiz
    correct_answers = 0
    total_questions = quiz.noOfQuestions
    responses = Response.objects.filter(Attempt=attempt)

    for response in responses:
        if response.Option.value == 1:  
            correct_answers += 1
    score = (correct_answers / total_questions) * quiz.maxMarks if total_questions else 0

    attempt.score = score
    attempt.save()
    context = {
        'quiz': quiz,  
        'attempt': attempt,
        'user_score': int(score),  
        'score': int(score),  
        'total_marks': 1,  
        'correct_answers': correct_answers,  
        'total_questions': total_questions,  
    }

    return render(request, 'decodeschool/quiz_results.html', context)
    



def clear_session(request):
    
    if 'shuffled_questions' in request.session:
        del request.session['shuffled_questions']
    if 'attempt_id' in request.session:
        del request.session['attempt_id']
    return JsonResponse({"status": "success"})
    
    

@login_required
def create_questions(request):
    
        QuestionFormSet = modelformset_factory(
            Question,
            form=QuestionForm,
            extra=1
        )

        if request.method == 'POST':
      
            total_forms = int(request.POST.get('questions-TOTAL_FORMS', 0))
            
            question_formset = QuestionFormSet(request.POST, prefix='questions')

            if question_formset.is_valid():
                saved_questions = []
                
                for i in range(total_forms):
                    try:
                        if request.POST.get(f'questions-{i}-DELETE') == 'on':
                            continue

                        name = request.POST.get(f'questions-{i}-name', '').strip()
                        if not name:
                            continue  # Skip empty forms

                        description = request.POST.get(f'questions-{i}-description', '')
                        answer_description = request.POST.get(f'questions-{i}-answer_description', '')
                        camp_category = request.POST.get(f'questions-{i}-camp_category', '')

                        try:
                            skill_id = int(request.POST.get(f'questions-{i}-skill', ''))
                            skill = Skill.objects.get(id=skill_id)
                        except (ValueError, Skill.DoesNotExist):
                            messages.error(request, f"Invalid skill for question {i}.")
                            continue

                        try:
                            tags_id = int(request.POST.get(f'questions-{i}-tags', ''))
                            tags = Tags.objects.get(id=tags_id)
                        except (ValueError, Tags.DoesNotExist):
                            messages.error(request, f"Invalid tag for question {i}.")
                            continue

                        is_practice = request.POST.get(f'questions-{i}-is_practice') == 'on'
                        question_id = request.POST.get(f'questions-{i}-id', '')

                        if question_id:
                            try:
                                question = Question.objects.get(id=question_id)
                                question.name = name
                                question.description = description
                                question.answer_description = answer_description
                                question.camp_category = camp_category
                                question.skill = skill
                                question.tags = tags
                                question.is_practice = is_practice
                                question.save()
                            except Question.DoesNotExist:
                                messages.error(request, f"Question {i} not found.")
                                continue
                            except Exception as e:
                                messages.error(request, f"Error updating question {i}: {str(e)}")
                                continue
                        else:
                            try:
                                question = Question.objects.create(
                                    name=name,
                                    description=description,
                                    answer_description=answer_description,
                                    camp_category=camp_category,
                                    skill=skill,
                                    tags=tags,
                                    is_practice=is_practice
                                )
                            except Exception as e:
                                messages.error(request, f"Error creating question {i}: {str(e)}")
                                continue

                       
                        saved_questions.append((i, question))
                    except Exception as e:
                        messages.error(request, f"Unexpected error processing question {i}: {str(e)}")
                
                # Handling options for each question
                for form_index, question in saved_questions:
                    try:
                        options_count = int(request.POST.get(f'questions-{form_index}-option_count', 0))
                        print(f"Processing {options_count} options for question {form_index} (ID: {question.id})")

                        for j in range(options_count):
                            try:
                                option_name = request.POST.get(f'questions-{form_index}-option-{j}-name', '').strip()
                                option_value = request.POST.get(f'questions-{form_index}-option-{j}-value', 0)

                                if not option_name:
                                    print(f"Skipping empty option {j} for question {question.id}")
                                    continue

                         
                                option_value = int(option_value)
                                

                                Option.objects.create(
                                    name=option_name,
                                    value=option_value,
                                    question=question
                                )
                              
                            except Exception as e:
                                messages.error(request, f"Error processing option {j} for question {form_index}: {str(e)}")
                    except Exception as e:
                        messages.error(request, f"Unexpected error processing options for question {form_index}: {str(e)}")

                messages.success(request, "Questions created successfully!")
                return redirect('aura_page')

            else:
                messages.error(request, "Form validation failed.")
                print("Form errors:", question_formset.errors)
        
        else:
            question_formset = QuestionFormSet(queryset=Question.objects.none(), prefix='questions')

        skills = Skill.objects.all()
       
        tags = Tags.objects.all()
        
        return render(request, 'decodeschool/add_multiple_questions.html', {
            'question_formset': question_formset,
            'skills': skills,
            'tags': tags,
        })




@login_required
def add_skill(request):
    
        if request.method != "POST":
         data = json.loads(request.body)
        skill_name = data.get('skill', '').strip()
        if not skill_name:
            return JsonResponse({'success': False, 'error': 'Skill name is required'}, status=400)
        if Skill.objects.filter(skill=skill_name).exists():
            return JsonResponse({'success': False, 'error': 'Skill already exists'}, status=400)
        skill = Skill.objects.create(skill=skill_name)
        return JsonResponse({'success': True, 'id': skill.id, 'name': skill.skill})


@login_required
def add_tag(request):
   
        data = json.loads(request.body)
        tag_name = data.get('tag', '').strip()
        if not tag_name:
            return JsonResponse({'success': False, 'error': 'Tag name is required'}, status=400)

        if Tags.objects.filter(tag=tag_name).exists():
            return JsonResponse({'success': False, 'error': 'Tag already exists'}, status=409)
      
        tag = Tags.objects.create(tag=tag_name)
      

        return JsonResponse({
            'success': True,
            'id': tag.id,
            'name': tag.tag
        }, status=201)

   


@login_required
def generate_pdf(request, attempt_id):
    # Fetch attempt record safely
    attempt = get_object_or_404(Attempt, id=attempt_id)

    # Sanitize quiz name for a safe filename
    quiz_name = re.sub(r'[^a-zA-Z0-9_-]', '_', attempt.quiz.name)

    # Create HttpResponse object to serve PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quiz_{quiz_name}_report.pdf"'

    # Create PDF canvas
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y_position = height - 80

    # Set Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.blue)
    pdf.drawString(180, height - 50, f" Report for {quiz_name} Quiz")

    # Draw line separator
    pdf.setStrokeColor(colors.gray)
    pdf.setLineWidth(1)
    pdf.line(50, height - 60, width - 50, height - 60)

    # Fetch responses for the attempt
    responses = Response.objects.filter(Attempt=attempt)

    styles = getSampleStyleSheet()
    styleN = styles['Normal']

    for idx, response_obj in enumerate(responses, start=1):
        question = response_obj.Question
        selected_option = response_obj.Option
        correct_option = Option.objects.filter(question=question, value=1).first()

        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColor(colors.black)
        question_text = f"{idx}. {question.name}"
        pdf.drawString(50, y_position, question_text)
        y_position -= 20

        # Draw options
        pdf.setFont("Helvetica", 11)
        options = Option.objects.filter(question=question)
        for opt in options:
            if opt == correct_option:
                pdf.setFillColor(colors.green)
                status = " ✅"
            elif opt == selected_option:
                pdf.setFillColor(colors.red)
                status = " ❌"
            else:
                pdf.setFillColor(colors.black)
                status = ""

            pdf.drawString(70, y_position, f"○ {opt.name}{status}")
            y_position -= 20

        # Add space before answer description
        y_position -= 10
        # Write answer description
        pdf.setFont("Helvetica-Oblique", 10)
        if question.answer_description:
            answer_para = Paragraph(f"<b>📌 Answer Description:</b> {question.answer_description}", styleN)
            answer_para.wrapOn(pdf, width - 100, height)
            answer_para.drawOn(pdf, 50, y_position)
            y_position -= answer_para.height + 10

        # Check if there's enough space for the next question
        if y_position < 100:
            pdf.showPage()
            y_position = height - 50

    pdf.save()
    return response

   