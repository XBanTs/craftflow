from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.db.models import Q, Sum, Avg
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job, Bid, SavedJob, Review, BidDraft
from .forms import JobForm, BidForm
from accounts.models import FreelancerProfile
from datetime import timedelta
from django.utils import timezone
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
    # Base queryset: active jobs only
    jobs = Job.objects.filter(status__in=['open', 'in_progress'])

    # --- Existing filters ---
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    budget_min = request.GET.get('budget_min', '')
    budget_max = request.GET.get('budget_max', '')
    sort = request.GET.get('sort', '-created_at')

    # --- New filters: status and posted_within ---
    status_filter = request.GET.get('status', '')
    posted_within = request.GET.get('posted_within', '')

    # Text search
    if query:
        from django.db.models import Q
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Category
    if category:
        jobs = jobs.filter(category=category)

    # Budget range
    if budget_min:
        try:
            jobs = jobs.filter(budget__gte=float(budget_min))
        except ValueError:
            pass
    if budget_max:
        try:
            jobs = jobs.filter(budget__lte=float(budget_max))
        except ValueError:
            pass

    # Status filter (allow to show only open or in_progress explicitly)
    if status_filter in ['open', 'in_progress']:
        jobs = jobs.filter(status=status_filter)

    # Posted within filter
    now = timezone.now()
    if posted_within == '24h':
        jobs = jobs.filter(created_at__gte=now - timedelta(hours=24))
    elif posted_within == '7d':
        jobs = jobs.filter(created_at__gte=now - timedelta(days=7))
    elif posted_within == '30d':
        jobs = jobs.filter(created_at__gte=now - timedelta(days=30))

    # Sorting
    valid_sorts = ['-created_at', 'created_at', 'budget', '-budget']
    if sort not in valid_sorts:
        sort = '-created_at'
    jobs = jobs.order_by(sort)

    jobs = jobs.select_related('client')

    # Saved job IDs
    saved_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = list(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    # Get client ratings for job cards
    from .utils import get_client_ratings
    client_ratings, client_review_counts = get_client_ratings(jobs)

    category_choices = Job.Category.choices
    context = {
        'jobs': jobs,
        'saved_job_ids': saved_job_ids,
        'query': query,
        'category': category,
        'budget_min': budget_min,
        'budget_max': budget_max,
        'sort': sort,
        'status_filter': status_filter,
        'posted_within': posted_within,
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

        # Get review for this job (if any)
    review = Review.objects.filter(job=job).first()

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
        'review': review,
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

    if job.client == request.user:
        messages.error(request, 'You cannot bid on your own job.')
        return redirect('job_detail', pk=job_pk)

    if job.status != 'open':
        messages.error(request, 'This job is no longer open for bidding.')
        return redirect('job_detail', pk=job_pk)

    if Bid.objects.filter(job=job, freelancer=request.user).exists():
        messages.error(request, 'You have already submitted a bid for this job.')
        return redirect('job_detail', pk=job_pk)

    # Check for existing draft
    draft = BidDraft.objects.filter(user=request.user, job=job).first()

    if request.method == 'POST':
        # Determine which button was clicked: 'submit' or 'save_draft'
        action = request.POST.get('action', 'submit')

        form = BidForm(request.POST)
        if form.is_valid():
            if action == 'save_draft':
                # Save as draft
                draft_data = form.cleaned_data
                BidDraft.objects.update_or_create(
                    user=request.user,
                    job=job,
                    defaults={
                        'amount': draft_data['amount'],
                        'proposal': draft_data['proposal'],
                    }
                )
                messages.success(request, 'Your proposal has been saved as a draft.')
                return redirect('job_detail', pk=job_pk)
            else:
                # Submit the bid
                bid = form.save(commit=False)
                bid.job = job
                bid.freelancer = request.user
                bid.status = 'pending'
                bid.save()
                # Delete any existing draft
                if draft:
                    draft.delete()
                messages.success(request, 'Your bid has been submitted successfully!')
                return redirect('job_detail', pk=job_pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre‑fill form from draft if exists
        initial = {}
        if draft:
            initial['amount'] = draft.amount
            initial['proposal'] = draft.proposal
        form = BidForm(initial=initial)

    return render(request, 'marketplace/bid_form.html', {
        'form': form,
        'job': job,
        'draft': draft,
    })


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


@login_required
def my_bids(request):
    """List all bids made by the logged-in freelancer, with edit/delete actions."""
    bids = Bid.objects.filter(freelancer=request.user).select_related('job').order_by('-created_at')
    return render(request, 'marketplace/my_bids.html', {'bids': bids})


@login_required
def bid_edit(request, pk):
    """Edit a pending bid."""
    bid = get_object_or_404(Bid, pk=pk, freelancer=request.user, status='pending')
    if request.method == 'POST':
        form = BidForm(request.POST, instance=bid)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bid updated successfully.')
            return redirect('my_bids')
    else:
        form = BidForm(instance=bid)
    return render(request, 'marketplace/bid_edit.html', {
        'form': form,
        'bid': bid,
        'job': bid.job,
    })


@login_required
def bid_delete(request, pk):
    """Delete a pending bid."""
    bid = get_object_or_404(Bid, pk=pk, freelancer=request.user, status='pending')
    if request.method == 'POST':
        bid.delete()
        messages.success(request, 'Bid deleted.')
        return redirect('my_bids')
    return render(request, 'marketplace/bid_confirm_delete.html', {'bid': bid}) 

