from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.db.models import Q, Sum, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job, Bid, SavedJob, Review
from .forms import JobForm, BidForm
from accounts.models import FreelancerProfile
from .utils import get_client_ratings


def home(request):
    """
    Public homepage — shows latest open jobs and a call to action.
    """
    recent_jobs = Job.objects.filter(status='open').order_by('-created_at')[:6]
    open_jobs = Job.objects.filter(status='open').count()
    freelancer_count = FreelancerProfile.objects.count()
    saved_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = list(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))
    # client ratings
    client_ratings, client_review_counts = get_client_ratings(recent_jobs)
    return render(request, 'marketplace/home.html', {
        'recent_jobs': recent_jobs,
        'open_jobs': open_jobs,
        'freelancer_count': freelancer_count,
        'saved_job_ids': saved_job_ids,
        'client_ratings': client_ratings,
        'client_review_counts': client_review_counts,
    })


def job_list(request):
    # Base queryset: only active jobs
    jobs = Job.objects.filter(status__in=['open', 'in_progress'])

    # --- Filtering ---
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    budget_min = request.GET.get('budget_min', '')
    budget_max = request.GET.get('budget_max', '')
    sort = request.GET.get('sort', '-created_at')  # default newest

    # Text search
    if query:
        from django.db.models import Q
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Category filter
    if category:
        jobs = jobs.filter(category=category)

    # Budget range filter
    if budget_min:
        try:
            min_val = float(budget_min)
            jobs = jobs.filter(budget__gte=min_val)
        except ValueError:
            pass
    if budget_max:
        try:
            max_val = float(budget_max)
            jobs = jobs.filter(budget__lte=max_val)
        except ValueError:
            pass

    # Sorting
    valid_sorts = ['-created_at', 'created_at', 'budget', '-budget']
    if sort not in valid_sorts:
        sort = '-created_at'
    jobs = jobs.order_by(sort)

    # Optimize query
    jobs = jobs.select_related('client')

    # Get saved job IDs for current user
    saved_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = list(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    # Prepare category choices for template
    category_choices = Job.Category.choices

    # client ratings
    client_ratings, client_review_counts = get_client_ratings(jobs)

    context = {
        'jobs': jobs,
        'saved_job_ids': saved_job_ids,
        'query': query,
        'category': category,
        'budget_min': budget_min,
        'budget_max': budget_max,
        'sort': sort,
        'category_choices': category_choices,
        'client_ratings': client_ratings,
        'client_review_counts': client_review_counts,
    }
    return render(request, 'marketplace/job_list.html', context)


def job_detail(request, pk):
    """
    Public detail view for a single job (dynamic URL /jobs/<pk>/).
    Fetches job and its bids (with related freelancer User) in one efficient query.
    """
    job = get_object_or_404(Job, pk=pk)
    bids = job.bids.all().select_related('freelancer').order_by('-created_at')

    user_has_bid = False
    is_saved = False
    if request.user.is_authenticated:
        user_has_bid = Bid.objects.filter(job=job, freelancer=request.user).exists()
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()

    # Collect verified freelancer IDs among all bidders
    bidder_ids = bids.values_list('freelancer_id', flat=True)
    verified_ids = FreelancerProfile.objects.filter(
        user_id__in=bidder_ids, is_verified=True
    ).values_list('user_id', flat=True)
    verified_freelancer_ids = set(verified_ids)

    context = {
        'job': job,
        'bids': bids,
        'user_has_bid': user_has_bid,
        'is_saved': is_saved,
        'verified_freelancer_ids': verified_freelancer_ids,
    }
    return render(request, 'marketplace/job_detail.html', context)



@login_required
def job_create(request):
    """
    POST a new job. Only authenticated clients can create.
    The client is set automatically to request.user.
    """
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            # commit=False gives us the Job instance without saving to DB yet.
            job.client = request.user
            job.save()
            messages.success(request, 'Your job has been posted successfully!')
            return redirect('job_detail', pk=job.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobForm()

    return render(request, 'marketplace/job_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def job_edit(request, pk):
    """
    Edit an existing job. Only the owner (job.client) can edit.
    Uses instance=job to pre-fill the form and update the existing record.
    """
    job = get_object_or_404(Job, pk=pk)

    # Security: only the job owner can edit
    if job.client != request.user:
        messages.error(request, 'You do not have permission to edit this job.')
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('job_detail', pk=job.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobForm(instance=job)

    return render(request, 'marketplace/job_form.html', {
        'form': form,
        'action': 'Edit',
        'job': job,
    })


@login_required
def job_delete(request, pk):
    """
    Delete a job. Only the owner can delete.
    Delete is a POST action — never GET.
    """
    job = get_object_or_404(Job, pk=pk)

    if job.client != request.user:
        messages.error(request, 'You do not have permission to delete this job.')
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully.')
        return redirect('job_list')

    return render(request, 'marketplace/job_confirm_delete.html', {'job': job})


@login_required
def dashboard(request):
    # ---------- Client Stats ----------
    client_jobs = Job.objects.filter(client=request.user)
    total_posted = client_jobs.count()
    open_client_jobs = client_jobs.filter(status='open').count()
    in_progress_client_jobs = client_jobs.filter(status='in_progress').count()
    completed_client_jobs = client_jobs.filter(status='completed')
    total_completed_client = completed_client_jobs.count()
    # Total amount spent on completed jobs (budgets of those jobs)
    total_spent = completed_client_jobs.aggregate(total=models.Sum('budget'))['total'] or 0

    # ---------- Freelancer Stats ----------
    freelancer_bids = Bid.objects.filter(freelancer=request.user)
    total_bids = freelancer_bids.count()
    active_bids = freelancer_bids.filter(status='pending').count()
    accepted_bids = freelancer_bids.filter(status='accepted')
    total_accepted = accepted_bids.count()
    # Completed projects where freelancer's accepted bid is on a completed job
    completed_projects = accepted_bids.filter(job__status='completed')
    total_completed_freelancer = completed_projects.count()
    # Total earned (sum of accepted bid amounts on completed projects)
    total_earned = completed_projects.aggregate(total=models.Sum('amount'))['total'] or 0
    # Completion rate (percentage of accepted bids that ended in completed jobs)
    completion_rate = (total_completed_freelancer / total_accepted * 100) if total_accepted > 0 else 0
    # Average rating received
    reviews_received = Review.objects.filter(reviewee=request.user)
    avg_rating = reviews_received.aggregate(avg=models.Avg('rating'))['avg'] or 0
    review_count = reviews_received.count()

    # ---------- General Activity ----------
    # Recent bids (for freelancers) or recent jobs posted (for clients)
    recent_activity = []
    if total_bids > 0:
        recent_activity = freelancer_bids.select_related('job').order_by('-created_at')[:5]
    elif total_posted > 0:
        recent_activity = client_jobs.order_by('-created_at')[:5]

    # ---------- Recommended Jobs (existing) ----------
    open_jobs_count = Job.objects.filter(status='open').count()
    recommended_jobs = Job.objects.filter(status='open').exclude(client=request.user).order_by('-created_at')[:5]

    # ---------- Saved Job Count ----------
    saved_count = SavedJob.objects.filter(user=request.user).count()

    # ---------- Saved Job IDs (for bookmark icons) ----------
    saved_job_ids = list(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    # ---------- Profile Completion Check ----------
    try:
        profile = request.user.freelancer_profile
        profile_incomplete = not all([profile.bio, profile.skills])
    except FreelancerProfile.DoesNotExist:
        profile_incomplete = True

    # client ratings
    client_ratings, client_review_counts = get_client_ratings(recommended_jobs)    

    context = {
        # Client
        'total_posted': total_posted,
        'open_client_jobs': open_client_jobs,
        'in_progress_client_jobs': in_progress_client_jobs,
        'total_completed_client': total_completed_client,
        'total_spent': total_spent,
        # Freelancer
        'total_bids': total_bids,
        'active_bids': active_bids,
        'total_accepted': total_accepted,
        'total_completed_freelancer': total_completed_freelancer,
        'total_earned': total_earned,
        'completion_rate': completion_rate,
        'avg_rating': avg_rating,
        'review_count': review_count,
        # General
        'recent_activity': recent_activity,
        'open_jobs_count': open_jobs_count,
        'recommended_jobs': recommended_jobs,
        'saved_count': saved_count,
        'saved_job_ids': saved_job_ids,
        'profile_incomplete': profile_incomplete,
        'client_ratings': client_ratings,
        'client_review_counts': client_review_counts,
    }
    return render(request, 'marketplace/dashboard.html', context)

@login_required
def bid_create(request, job_pk):
    """
    Allows a freelancer to submit a bid on a job.
    - Only open jobs can receive bids.
    - The bidder cannot be the job client.
    - Only one bid per freelancer per job.
    """
    job = get_object_or_404(Job, pk=job_pk)
    if job.status != 'open':
        messages.error(request, 'This job is not open for bidding.')
        return redirect('job_detail', pk=job_pk)
    if job.client == request.user:
        messages.error(request, 'You cannot bid on your own job.')
        return redirect('job_detail', pk=job_pk)
    if Bid.objects.filter(job=job, freelancer=request.user).exists():
        messages.error(request, 'You have already submitted a bid for this job.')
        return redirect('job_detail', pk=job_pk)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.job = job
            bid.freelancer = request.user
            bid.status = 'pending'
            bid.save()
            messages.success(request, 'Your bid has been submitted!')
            return redirect('job_detail', pk=job_pk)
    else:
        form = BidForm()
    return render(request, 'marketplace/bid_form.html', {'form': form, 'job': job})


@login_required
def save_job_toggle(request, job_pk):
    """
    Toggle: if the user hasn't saved the job, save it.
    If they already saved it, unsave it.
    """
    job = get_object_or_404(Job, pk=job_pk)
    user = request.user

    # Try to find an existing saved record
    saved = SavedJob.objects.filter(user=user, job=job).first()
    if saved:
        saved.delete()
        messages.success(request, f'Removed "{job.title}" from saved jobs.')
    else:
        SavedJob.objects.create(user=user, job=job)
        messages.success(request, f'Saved "{job.title}" for later.')

    # Redirect back to the previous page (or job detail)
    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('job_detail', pk=job_pk)


@login_required
def saved_jobs(request):
    """
    Show all jobs saved by the current user.
    """
    saved_entries = SavedJob.objects.filter(
        user=request.user
    ).select_related('job__client').order_by('-created_at')

    # Extract the actual Job objects (already loaded)
    saved_jobs_list = [entry.job for entry in saved_entries]

    # Pass an empty saved_job_ids list because all displayed jobs are saved
    context = {
        'jobs': saved_jobs_list,
        'saved_job_ids': [job.pk for job in saved_jobs_list],  # all are saved
    }
    return render(request, 'marketplace/saved_jobs.html', context)    
