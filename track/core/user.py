from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from track.forms import UserForm
from track.views import check_coordinator, check_admin
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import HttpResponseRedirect

def list_users(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(username__icontains=search_query).order_by('username') | User.objects.filter(first_name__icontains=search_query).order_by('username')
    groups = Group.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj, 
        'search_query': search_query,
        'groups' : groups
    }
    return render(request, 'decodeschool/users.html', context)

@csrf_exempt
@user_passes_test(check_admin) 
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = get_random_string(length=8)
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        send_mail('Your Account Password for COMPASS', f'Your User Name is {username} \n Your password for Compass Portal is {password}', None, [email])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
@user_passes_test(check_admin) 
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Process the submitted form
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'User updated successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Render the form with the object data
        form = UserForm(instance=user)
        return JsonResponse({'success': True, 'form': form.as_p()})

@csrf_exempt
@user_passes_test(check_admin) 
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    password = get_random_string(length=8)
    user.set_password(password)
    user.save()
    send_mail('Password Reset', f'Your new password is {password}', 'admin@example.com', [user.email])
    return JsonResponse({'success': True})

@user_passes_test(check_admin) 
def assign_group(request):
    data = dict()
    username = request.GET.get('username')
    groupname = request.GET.get('groupname')
    
    user = User.objects.get(username=username)
    group = Group.objects.get(name=groupname)
   

    if user.groups.filter(name=groupname).exists():
        group.user_set.remove(user)
        data['message'] = "successfully removed"
    else:
        group.user_set.add(user)
        data['message'] = "successfully Added"
    
    return JsonResponse(data)


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            new_password = get_random_string(length=8)
            user.password = make_password(new_password)  # Hash the password before saving
            user.save()

            # Send the email with the new password
            send_mail(
                'Your New Password',
                f'Hi {user.first_name},\n\nYour new password is: {new_password}\n\nPlease change your password after logging in.',
                'noreply@example.com',  # Replace with your sender email
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'A new password has been sent to your email.')
        except User.DoesNotExist:
            messages.error(request, 'User with this username does not exist.')

        return HttpResponseRedirect(reverse('forgot_password'))

    return render(request, 'decodeschool/forgot_password.html')
