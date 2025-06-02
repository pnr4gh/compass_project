from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from track.models import Profile, User_Handle, Platform
from django.contrib.auth.models import User
from track.forms import ProfileForm, UserHandleForm, UserForm, UserEditForm  # Assuming UserForm for editing user data
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def user_profile(request):
    # Fetch user's profile and user handles
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    user_handles = User_Handle.objects.filter(user=user)
    platforms = Platform.objects.all()

    if request.method == "POST":
        # Update User and Profile
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')
        else:
            # Re-render the page with errors
            return render(request, 'decodeschool/user_profile.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user_handles': user_handles,
                'platforms': platforms
            })

    # Render the profile page
    return render(request, 'decodeschool/user_profile.html', {
        'user_form': UserEditForm(instance=user),
        'profile_form': ProfileForm(instance=profile),
        'user_handles': user_handles,
        'platforms': platforms
    })


@login_required
def add_user_handle(request):
    if request.method == "POST":
        form = UserHandleForm(request.POST)
        
        if form.is_valid():
            if not User_Handle.objects.filter(user=request.user, platform=request.POST.get('platform')).exists():
                user_handle = form.save(commit=False)
                user_handle.user = request.user  # Assign to the current user
                user_handle.save()
                return JsonResponse({'message': 'User handle added successfully'}, status=200)
            else:
                return JsonResponse({'message': 'User handle already added for this platform'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def remove_user_handle(request):
    if User_Handle.objects.filter(user=request.user, platform__id=request.GET.get('platform')).exists():
        User_Handle.objects.filter(user=request.user, platform__id=request.GET.get('platform')).delete()
        return JsonResponse({'message': 'User handle removed successfully'}, status=200)
    else:
        return JsonResponse({'message': 'No such User Handle'}, status=200)