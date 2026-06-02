from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from marketplace.models import Bid, Review
from .forms import CustomUserRegistrationForm, FreelancerProfileEditForm, PortfolioItemForm
from .models import FreelancerProfile, PortfolioItem, UserVerification
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import uuid


def register_view(request):
    """
    Handles new user registration.

    GET: Display an empty registration form.
    POST: Validate the form. If valid, create the user, log them in,
          and redirect to home. If invalid, re-render with errors.

    The Post/Redirect/Get (PRG) pattern:
    - On successful POST, we redirect to another page.
    - This prevents the browser's "Confirm Form Resubmission" dialog
      if the user refreshes the page.
    - It also prevents accidental double-submission.
    """
    if request.user.is_authenticated:
        # If the user is already logged in, redirect them to home.
        # No reason to show the registration page to authenticated users.
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # form.save() returns the newly created User instance.
            # The password is already hashed at this point.

                        # Create verification record
            verification = UserVerification.objects.create(user=user)

            # Build verification URL
            verify_url = request.build_absolute_uri(
                reverse('verify_email', args=[str(verification.token)])
            )

            # Send verification email
            send_mail(
                subject='Verify your CraftFlow account',
                message=f'Welcome to CraftFlow!\n\nPlease verify your email by clicking the link below:\n{verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Log user in (but can restrict later if desired)
            login(request, user)
            messages.success(request, f'Welcome to CraftFlow, {user.username}! Please check your email to verify your account.')

            # Log the user in immediately after registration.
            # This is a UX decision: don't force them to log in after signing up.
            login(request, user)

            messages.success(
                request,
                f'Welcome to CraftFlow, {user.username}! Your account has been created.'
            )
            return redirect('dashboard')
        else:
            # The form is invalid — Django has already populated form.errors.
            # We add a generic error message for the user.
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handles user login.

    We use Django's built-in AuthenticationForm for validation,
    but implement the view as a function for consistency and clarity.

    AuthenticationForm:
    - Checks that the username exists and the password matches.
    - If not, raises a ValidationError on the whole form.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # AuthenticationForm takes 'request' as the first positional argument
        # because it uses request.session for security (login rate limiting).
        # data=request.POST must be passed as a keyword argument.

        if form.is_valid():
            # form.get_user() returns the authenticated User object.
            # This user has already been verified by authenticate() inside the form.
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Handles user logout.

    We use Django's built-in logout function.
    This flushes the user's session, removing all session data.
    """
    if request.method == 'POST':
        logout(request)
        # logout() clears the session and removes the user from request.
        messages.success(request, 'You have been logged out.')
        return redirect('home')

    # If someone navigates to /accounts/logout/ via GET, show them the home page.
    # Logout should only happen via POST.
    return redirect('home')


@login_required
def profile_view(request, pk):
    """
    Displays a user's profile.

    Protected by @login_required: only authenticated users can view profiles.
    The 'pk' in the URL is the User's primary key.
    """
    profile_user = get_object_or_404(User, pk=pk)

    # Freelancer profile
    try:
        freelancer_profile = profile_user.freelancer_profile
    except FreelancerProfile.DoesNotExist:
        freelancer_profile = None

    # ---------- Freelancer Stats ----------
    accepted_bids = Bid.objects.filter(freelancer=profile_user, status='accepted')
    total_accepted = accepted_bids.count()
    completed_bids = accepted_bids.filter(job__status='completed')
    total_completed = completed_bids.count()
    total_earned = completed_bids.aggregate(total=Sum('amount'))['total'] or 0
    completion_rate = (total_completed / total_accepted * 100) if total_accepted > 0 else 0

    # Reviews
    reviews_received = Review.objects.filter(reviewee=profile_user)
    avg_rating = reviews_received.aggregate(avg=Avg('rating'))['avg'] or 0
    review_count = reviews_received.count()

        # Portfolio items (only if freelancer profile exists)
    portfolio_items = []
    if freelancer_profile:
        portfolio_items = PortfolioItem.objects.filter(user=profile_user).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'freelancer_profile': freelancer_profile,
        'total_completed': total_completed,
        'total_earned': total_earned,
        'completion_rate': completion_rate,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'portfolio_items': portfolio_items,
    }
    return render(request, 'accounts/profile.html', context)

@staff_member_required
def admin_dashboard(request):
    """
    A simple dashboard visible only to staff members.

    @staff_member_required: only users with is_staff=True can access this view.
    Regular users are redirected to the admin login page.

    This satisfies the Brief's requirement: at least one action restricted to
    staff or admin users only.
    """
    # We can add summary stats here later.
    total_jobs = 0
    total_users = 0

    # We'll import models inside the function to avoid circular imports,
    # or import at the top. For now, we keep it simple.
    from marketplace.models import Job
    from django.contrib.auth.models import User

    total_jobs = Job.objects.count()
    total_users = User.objects.count()

    context = {
        'total_jobs': total_jobs,
        'total_users': total_users,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def profile_edit_view(request, pk):
    # Ensure users can only edit their own profile
    if request.user.pk != pk:
        messages.error(request, 'You can only edit your own profile.')
        return redirect('profile', pk=request.user.pk)

    # Get or create the freelancer profile
    profile, created = FreelancerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = FreelancerProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile', pk=request.user.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FreelancerProfileEditForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Portfolio item added.')
            return redirect('profile', pk=request.user.pk)
    else:
        form = PortfolioItemForm()
    return render(request, 'accounts/portfolio_form.html', {
        'form': form,
        'action': 'Add',
    })


@login_required
def portfolio_edit(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio item updated.')
            return redirect('profile', pk=request.user.pk)
    else:
        form = PortfolioItemForm(instance=item)
    return render(request, 'accounts/portfolio_form.html', {
        'form': form,
        'action': 'Edit',
        'item': item,
    })


@login_required
def portfolio_delete(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Portfolio item deleted.')
        return redirect('profile', pk=request.user.pk)
    return render(request, 'accounts/portfolio_confirm_delete.html', {
        'item': item,
    })    


def verify_email(request, token):
    verification = get_object_or_404(UserVerification, token=token)
    if not verification.email_verified:
        verification.email_verified = True
        verification.save()
        # Optionally activate user if you want to restrict login before verification
        # verification.user.is_active = True
        # verification.user.save()
        messages.success(request, 'Your email has been verified. Thank you!')
    else:
        messages.info(request, 'Your email was already verified.')
    return redirect('dashboard')    


@login_required
def resend_verification(request):
    user = request.user
    # Get or create verification record
    verification, created = UserVerification.objects.get_or_create(user=user)
    if verification.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard')

    # Generate new token
    verification.token = uuid.uuid4()
    verification.save()

    verify_url = request.build_absolute_uri(
        reverse('verify_email', args=[str(verification.token)])
    )
    send_mail(
        subject='Verify your CraftFlow account',
        message=f'Please verify your email by clicking the link below:\n{verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    messages.success(request, 'A new verification email has been sent.')
    return redirect('dashboard')    