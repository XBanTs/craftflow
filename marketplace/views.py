from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job, Bid
from .forms import JobForm, BidForm
from accounts.models import FreelancerProfile


def home(request):
    """
    Public homepage — shows latest open jobs and a call to action.
    """
    recent_jobs = Job.objects.filter(status='open').order_by('-created_at')[:6]
    open_jobs = Job.objects.filter(status='open').count()
    freelancer_count = FreelancerProfile.objects.count()
    return render(request, 'marketplace/home.html', {
        'recent_jobs': recent_jobs,
        'open_jobs': open_jobs,
        'freelancer_count': freelancer_count,
    })


def job_list(request):
    """
    Public list of all open jobs, newest first.
    Uses select_related('client') to avoid N+1 queries when accessing
    job.client.username in the template.
    """
    jobs = Job.objects.filter(status='open').order_by('-created_at').select_related('client')
    return render(request, 'marketplace/job_list.html', {'jobs': jobs})


def job_detail(request, pk):
    """
    Public detail view for a single job (dynamic URL /jobs/<pk>/).
    Fetches job and its bids (with related freelancer User) in one efficient query.
    """
    job = get_object_or_404(Job, pk=pk)

    bids = (
        job.bids.all()
        .select_related('freelancer')
        .order_by('-created_at')
    )

    # Check if the logged-in user has already placed a bid on this job
    user_has_bid = False

    if request.user.is_authenticated:
        user_has_bid = Bid.objects.filter(
            job=job,
            freelancer=request.user
        ).exists()

    context = {
        'job': job,
        'bids': bids,
        'user_has_bid': user_has_bid,
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
    # As client: jobs you posted
    client_jobs = Job.objects.filter(client=request.user).order_by('-created_at')
    # As freelancer: your bids
    freelancer_bids = Bid.objects.filter(freelancer=request.user).select_related('job').order_by('-created_at')
    # Overall platform stats
    total_jobs = Job.objects.count()
    open_jobs = Job.objects.filter(status='open').count()
    # Recommended jobs: latest open ones not posted by user
    recommended_jobs = Job.objects.filter(status='open').exclude(client=request.user).order_by('-created_at')[:5]

    context = {
        'client_jobs': client_jobs,
        'freelancer_bids': freelancer_bids,
        'total_jobs': total_jobs,
        'open_jobs': open_jobs,
        'recommended_jobs': recommended_jobs,
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
