from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.core.paginator import Paginator
from .models import Profile, ParentStudentDetails, TutorProfile, Rating
from .forms import CustomUserCreationForm, ParentStudentDetailsForm, TutorProfileForm, TutorSearchForm, RatingForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

# Signal to create or update the Profile whenever a User is created or saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    print(f"Signal triggered for user: {instance.username}")
    print(f"Created: {created}")
    
    # Only create profile if it doesn't exist
    if not hasattr(instance, 'profile'):
        print("Creating new profile")
        Profile.objects.create(user=instance)
        print(f"Profile created for user {instance.username}")
        
@require_http_methods(["POST"])
def reset_password(request):
    username = request.POST.get("username")
    new_password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")
    
    try:
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect(reverse("auth_page") + "?reset_error=user_not_found")

        # Validate passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse("auth_page") + "?reset_error=passwords_mismatch")

        # Validate password complexity
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            messages.error(request, f"Password validation error: {', '.join(e.messages)}")
            return redirect(reverse("auth_page") + "?reset_error=validation_failed")

        # Check if new password is different from current
        if user.check_password(new_password):
            messages.error(request, "New password must be different from current password.")
            return redirect(reverse("auth_page") + "?reset_error=same_password")

        # Set new password
        user.set_password(new_password)
        user.save()

        messages.success(request, "Password has been reset successfully. Please login with your new password.")
        return redirect(reverse("auth_page") + "?reset_success=true")

    except Exception as e:
        messages.error(request, "An error occurred while resetting your password. Please try again.")
        return redirect(reverse("auth_page") + "?reset_error=server_error")

# Unified Sign In/Sign Up View
def auth_page(request):
    register_form = CustomUserCreationForm()
    login_form = AuthenticationForm()
    show_forgot_password_modal = False

    if request.method == 'POST':
        # Handle Login
        if 'sign_in' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                # Authenticate and log in user
                user = login_form.get_user()
                login(request, user)
                return redirect('index')  # Redirect after successful login

            # Debug statement
            print("Login failed. Form errors:", login_form.errors)

            # If login fails, render with errors
            return render(request, 'edu/auth_page.html', {
                'register_form': CustomUserCreationForm(),  # Fresh register form
                'login_form': login_form,  # Preserve login errors
                'show_forgot_password_modal': show_forgot_password_modal,
            })

        # Handle Registration (preserved logic)
        # Inside auth_page view
        if 'sign_up' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                try:
                    print("Form data:", register_form.cleaned_data)
                    print("Selected role:", register_form.cleaned_data.get('role'))
                    
                    # Save user and profile
                    user = register_form.save()
                    
                    # Debug profile and role
                    print(f"User created: {user.username}")
                    print(f"Profile exists: {hasattr(user, 'profile')}")
                    print(f"Profile role: {user.profile.role}")
                    
                    # Login user
                    login(request, user)
                    
                    # Force refresh from database
                    user.refresh_from_db()
                    print(f"Role after refresh: {user.profile.role}")
                    
                    # Redirect based on role
                    if user.profile.role == 'parent_student':
                        print("Redirecting to parent dashboard")
                        return redirect('parent_dashboard')
                    elif user.profile.role == 'tutor_center':
                        print("Redirecting to tutor dashboard")
                        return redirect('tutor_dashboard')
                    else:
                        print(f"Unknown role ({user.profile.role}) - redirecting to index")
                        return redirect('index')
                        
                except Exception as e:
                    print(f"Registration error: {str(e)}")
                    messages.error(request, f"Registration failed: {str(e)}")
                    return render(request, 'edu/auth_page.html', {
                        'register_form': register_form,
                        'login_form': AuthenticationForm(),
                        'show_forgot_password_modal': False,
                    })

    # For GET requests, render the login/register page
    return render(request, 'edu/auth_page.html', {
        'register_form': register_form,
        'login_form': login_form,
        'show_forgot_password_modal': show_forgot_password_modal,
    })


    
# Home page view
def index(request):
    return render(request, 'edu/index.html')

# Logout view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('auth_page')

@login_required
def parent_dashboard(request):
    if request.user.profile.role != 'parent_student':
        messages.error(request, "You do not have access to this dashboard.")
        return redirect('index')

    try:
        details = request.user.parent_student_details
    except ParentStudentDetails.DoesNotExist:
        details = None

    edit_mode = request.GET.get('edit') == 'true'

    if request.method == 'POST':
        form = ParentStudentDetailsForm(request.POST, instance=details)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.user = request.user
            # Join selected favorite subjects into a string
            detail.favorite_subjects = ', '.join(request.POST.getlist('favorite_subjects'))
            detail.save()
            messages.success(request, "Details saved successfully!")
            return redirect('parent_dashboard')
    else:
        form = ParentStudentDetailsForm(instance=details)

    # Safely split favorite_subjects into a list for the template
    favorite_subjects_list = []
    if details and details.favorite_subjects:
        favorite_subjects_list = [subject.strip() for subject in details.favorite_subjects.split(',') if subject.strip()]

    return render(request, 'edu/parent_dashboard.html', {
        'details': details,
        'form': form,
        'edit_mode': edit_mode,
        'favorite_subjects_list': favorite_subjects_list,
    })

    
@login_required
def tutor_dashboard(request):
    if request.user.profile.role != "tutor_center":
        messages.error(request, "You do not have access to this dashboard.")
        return redirect("index")
    
    tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
    edit_mode = request.GET.get("edit") == "true"
    
    if request.method == "POST":
        form = TutorProfileForm(request.POST, request.FILES, instance=tutor_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            
            # Handle image upload if present
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                print(f"Received image file: {image_file.name}")
                print(f"Image file size: {image_file.size} bytes")
                print(f"Content type: {image_file.content_type}")
                
                # Validate file size (5MB limit)
                if image_file.size > 5 * 1024 * 1024:
                    messages.error(request, "Image file is too large. Maximum size is 5MB.")
                    return render(request, "edu/tutor_dashboard.html", {
                        "tutor_profile": tutor_profile,
                        "form": form,
                        "edit_mode": edit_mode,
                        "school_level_list": tutor_profile.school_level.split(", ") if tutor_profile.school_level else []
                    })
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/png', 'image/gif']
                if image_file.content_type not in allowed_types:
                    messages.error(request, "Please upload only JPEG, PNG, or GIF images.")
                    return render(request, "edu/tutor_dashboard.html", {
                        "tutor_profile": tutor_profile,
                        "form": form,
                        "edit_mode": edit_mode,
                        "school_level_list": tutor_profile.school_level.split(", ") if tutor_profile.school_level else []
                    })
                
                try:
                    # Reset file pointer to beginning and read the data
                    image_file.seek(0)
                    image_data = image_file.read()
                    print(f"Read image data size: {len(image_data)} bytes")
                    
                    profile.profile_image = image_data
                    profile.image_name = image_file.name
                    profile.image_type = image_file.content_type
                    
                    # Verify the data was assigned
                    print(f"Profile image data size after assignment: {len(profile.profile_image) if profile.profile_image else 0} bytes")
                    
                except Exception as e:
                    print(f"Error during image processing: {str(e)}")
                    messages.error(request, f"Error processing image: {str(e)}")
                    return redirect("tutor_dashboard")
            
            # Save selected school levels (keeping existing functionality)
            profile.school_level = ', '.join(form.cleaned_data["school_level"])
            
            try:
                profile.save()
                # Verify the data after save
                saved_profile = TutorProfile.objects.get(id=profile.id)
                print(f"Saved image data size: {len(saved_profile.profile_image) if saved_profile.profile_image else 0} bytes")
                
                messages.success(request, "Your tutor profile has been updated successfully!")
                return redirect("tutor_dashboard")
            except Exception as e:
                print(f"Error during save: {str(e)}")
                messages.error(request, f"Error saving profile: {str(e)}")
                return redirect("tutor_dashboard")
    else:
        form = TutorProfileForm(instance=tutor_profile)
    
    # Convert the saved string back into a list for the checkboxes
    school_level_list = []
    if tutor_profile.school_level:
        school_level_list = tutor_profile.school_level.split(", ")
    
    return render(
        request,
        "edu/tutor_dashboard.html",
        {
            "tutor_profile": tutor_profile,
            "form": form,
            "edit_mode": edit_mode,
            "school_level_list": school_level_list,
            "has_profile_image": bool(tutor_profile.profile_image)
        },
    )
    
@login_required
def profile_redirect(request):
    try:
        role = request.user.profile.role
        if role == 'parent_student':
            return redirect('parent_dashboard')
        elif role == 'tutor_center':
            return redirect('tutor_dashboard')
        else:
            return redirect('index')
    except Profile.DoesNotExist:
        return redirect('index')

def tutor_search(request):
    form = TutorSearchForm(request.GET or None)
    queryset = TutorProfile.objects.all()

    # Check if it's initial page load (no search parameters)
    is_initial_load = not any(request.GET.values())
    print(f"Is initial load: {is_initial_load}")

    if is_initial_load:
        if request.user.is_authenticated:
            try:
                print(f"User: {request.user.username}")
                print(f"User role: {request.user.profile.role}")  # Debug user role

                # Get user's city based on their role
                user_city = None
                if request.user.profile.role == 'parent_student':
                    if hasattr(request.user, 'parent_student_details'):
                        user_city = request.user.parent_student_details.city
                        print(f"Parent city: {user_city}")
                elif request.user.profile.role == 'tutor_center':
                    if hasattr(request.user, 'tutorprofile'):
                        user_city = request.user.tutorprofile.city
                        print(f"Tutor city: {user_city}")

                if user_city:
                    queryset = queryset.filter(city__iexact=user_city)
                    print(f"Filtered queryset count: {queryset.count()}")
                    print(f"SQL Query: {queryset.query}")
                    messages.info(request, f"Showing tutors in {user_city}")
                else:
                    print("No city found for user")
                    messages.info(request, "Showing all tutors - city not set in your profile")
            except Exception as e:
                print(f"Error in city search: {str(e)}")
                messages.error(request, "An error occurred while finding local tutors")
        else:
            messages.info(request, "Log in to see tutors in your area!")

    elif form.is_valid():
        # Your existing search logic
        location = form.cleaned_data.get('location')
        subjects_offered = form.cleaned_data.get('subjects_offered')
        school_level = form.cleaned_data.get('school_level')
        hourly_rate_min = form.cleaned_data.get('hourly_rate_min')
        hourly_rate_max = form.cleaned_data.get('hourly_rate_max')
        teaching_experience = form.cleaned_data.get('teaching_experience')
        specializations = form.cleaned_data.get('specializations')

        if location:
            queryset = queryset.filter(city__icontains=location)
        if subjects_offered:
            queryset = queryset.filter(subjects_offered__icontains=subjects_offered)
        if school_level:
            queryset = queryset.filter(school_level__icontains=school_level)
        if hourly_rate_min:
            queryset = queryset.filter(hourly_rate__gte=hourly_rate_min)
        if hourly_rate_max:
            queryset = queryset.filter(hourly_rate__lte=hourly_rate_max)
        if teaching_experience:
            queryset = queryset.filter(teaching_experience__gte=teaching_experience)
        if specializations:
            queryset = queryset.filter(specializations__icontains=specializations)

    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    profiles = paginator.get_page(page)

    return render(request, 'edu/tutor_search.html', {
        'form': form,
        'profiles': profiles,
    })
    
@login_required
def tutor_detail(request, id):
    tutor = get_object_or_404(TutorProfile, id=id)
    avg_rating = tutor.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    rating = Rating.objects.filter(tutor=tutor, user=request.user).first()
    can_rate = Rating.can_user_rate_tutor(request.user, tutor)

    if request.method == 'POST':
        # Check if user can rate before processing the form
        if not can_rate:
            next_available = rating.get_next_available_date()
            messages.error(
                request, 
                f"You can only review this tutor once every 3 months. You can submit another review after {next_available.strftime('%Y-%m-%d')}"
            )
            return redirect('tutor_detail', id=tutor.id)

        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.tutor = tutor
            new_rating.user = request.user
            new_rating.save()
            messages.success(request, "Your rating has been submitted successfully!")
            return redirect('tutor_detail', id=tutor.id)
        else:
            messages.error(request, "There was an error submitting your rating. Please try again.")
    else:
        form = RatingForm(instance=rating)

    # Get next available rating date if user can't rate
    next_available_date = None
    if not can_rate and rating:
        next_available_date = rating.get_next_available_date()

    return render(request, 'edu/tutor_detail.html', {
        'tutor': tutor,
        'form': form,
        'avg_rating': avg_rating,
        'can_rate': can_rate,
        'next_available_date': next_available_date,
        'user_rating': rating
    })
    

@login_required
def submit_rating(request, tutor_id):
    """
    View for submitting or updating a tutor rating
    """
    tutor = get_object_or_404(TutorProfile, id=tutor_id)
    
    # Check if user can rate this tutor
    if not Rating.can_user_rate_tutor(request.user, tutor):
        # Get the user's last rating for this tutor
        last_rating = Rating.objects.filter(
            tutor=tutor, 
            user=request.user
        ).first()
        next_available = last_rating.get_next_available_date()
        messages.error(
            request, 
            f"You can only review this tutor once every 3 months. You can submit another review after {next_available.strftime('%Y-%m-%d')}"
        )
        return redirect('tutor_detail', id=tutor.id)

    # Get existing rating if it exists
    rating = Rating.objects.filter(tutor=tutor, user=request.user).first()

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.tutor = tutor
            new_rating.user = request.user
            new_rating.save()
            messages.success(request, "Your rating has been submitted successfully!")
            return redirect('tutor_detail', id=tutor.id)
        else:
            messages.error(request, "There was an error submitting your rating. Please try again.")
    else:
        form = RatingForm(instance=rating)

    context = {
        'form': form, 
        'tutor': tutor,
        'is_update': rating is not None
    }
    return render(request, 'edu/submit_rating.html', context)

def reset_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect(reverse("auth_page"))

        # Validate that passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse("auth_page"))

        # Check if the new password is the same as the old one
        if user.check_password(new_password):
            messages.error(request, "The new password cannot be the same as the old password.")
            return redirect(reverse("auth_page"))

        # Validate password complexity
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            messages.error(request, f"Password validation error: {', '.join(e.messages)}")
            return redirect(reverse("auth_page"))

        # Save the new password
        user.set_password(new_password)
        user.save()

        messages.success(request, "Your password has been successfully reset.")
        return redirect(reverse("auth_page"))

    return redirect(reverse("auth_page"))

from django.http import HttpResponse, HttpResponseNotFound

def serve_tutor_image(request, tutor_id):
    try:
        tutor = TutorProfile.objects.get(id=tutor_id)
        if tutor.profile_image:
            return HttpResponse(
                tutor.profile_image,
                content_type=tutor.image_type or 'image/jpeg'
            )
        return HttpResponseNotFound("No image found")
    except TutorProfile.DoesNotExist:
        return HttpResponseNotFound("Tutor not found")