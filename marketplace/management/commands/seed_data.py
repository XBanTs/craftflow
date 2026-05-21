# marketplace/management/commands/seed_data.py
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import FreelancerProfile
from marketplace.models import Job, Bid, Review, Service


class Command(BaseCommand):
    help = 'Seeds the database with realistic, balanced marketplace data.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # ---------- Default superuser (for Render free tier) ----------
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@craftflow.com',
                password='Admin123!'
            )
            self.stdout.write('  → Created superuser: admin / Admin123!')
        else:
            self.stdout.write('  → Superuser already exists. Skipping.')

        # ---------- Users ----------
        # Create clients
        clients_data = [
            {'username': 'alice_startup', 'email': 'alice@startup.com'},
            {'username': 'bob_agency',   'email': 'bob@agency.com'},
            {'username': 'clara_found',  'email': 'clara@foundation.com'},
            {'username': 'dave_product', 'email': 'dave@product.com'},
        ]
        clients = []
        for data in clients_data:
            user, created = User.objects.get_or_create(username=data['username'], defaults={
                'email': data['email'],
            })
            if created:
                user.set_password('password123')
                user.save()
            clients.append(user)

        # Create freelancers
        freelancers_data = [
            {'username': 'frank_python',   'skills': 'Python, Django, REST APIs, PostgreSQL'},
            {'username': 'grace_design',   'skills': 'UI/UX Design, Figma, Prototyping'},
            {'username': 'henry_writer',   'skills': 'Technical Writing, Documentation, SEO'},
            {'username': 'irina_data',     'skills': 'Data Analysis, Pandas, SQL, Tableau'},
        ]
        freelancers = []
        for data in freelancers_data:
            user, created = User.objects.get_or_create(username=data['username'], defaults={
                'email': f'{data["username"]}@craftflow.com',
            })
            if created:
                user.set_password('password123')
                user.save()
            # FreelancerProfile
            profile, _ = FreelancerProfile.objects.get_or_create(user=user)
            profile.skills = data['skills']
            profile.bio = f'Experienced {data["skills"].split(",")[0].strip()} specialist.'
            profile.hourly_rate = Decimal(random.choice([35, 50, 75, 100, 120]))
            profile.save()
            freelancers.append(user)

        # ---------- Jobs ----------
        job_templates = [
            {
                'title': 'Build a REST API backend for mobile app',
                'description': 'We need a developer to build a secure REST API using Django or Node.js. Must include JWT auth and PostgreSQL integration.',
                'category': 'web_dev',
                'budget': 2000.00,
            },
            {
                'title': 'Design a modern SaaS dashboard UI',
                'description': 'Looking for a UI/UX designer to create a clean, modern dashboard for our B2B SaaS product. Figma files required.',
                'category': 'ui_ux',
                'budget': 1500.00,
            },
            {
                'title': 'Write technical documentation for API product',
                'description': 'We need a technical writer to produce comprehensive API docs (OpenAPI) and user guides.',
                'category': 'writing',
                'budget': 800.00,
            },
            {
                'title': 'Data analysis & visualization for sales report',
                'description': 'Analyse our Q1 sales data and produce an interactive Tableau dashboard with insights.',
                'category': 'data_science',
                'budget': 1200.00,
            },
            {
                'title': 'Fix critical bugs in Django e‑commerce site',
                'description': 'Our production Django site has several performance and payment integration bugs. Need immediate help.',
                'category': 'web_dev',
                'budget': 2500.00,
            },
            {
                'title': 'Redesign landing page & branding kit',
                'description': 'We want a complete visual overhaul of our landing page plus a small brand identity package.',
                'category': 'ui_ux',
                'budget': 1000.00,
            },
            {
                'title': 'SEO audit and content optimisation',
                'description': 'Perform a full SEO audit on our blog and optimise 20 articles for target keywords.',
                'category': 'marketing',
                'budget': 600.00,
            },
            {
                'title': 'Build a Telegram bot for customer support',
                'description': 'Develop a Telegram bot that integrates with our helpdesk API and provides automatic replies.',
                'category': 'web_dev',
                'budget': 1800.00,
            },
        ]

        jobs = []
        for template in job_templates:
            client = random.choice(clients)
            job = Job.objects.create(
                title=template['title'],
                description=template['description'],
                budget=template['budget'],
                category=template['category'],
                client=client,
                status='open',
            )
            jobs.append(job)

        # Set one job to in_progress and one to completed (with review)
        in_progress_job = jobs[0]
        in_progress_job.status = 'in_progress'
        in_progress_job.save()
        completed_job = jobs[1]
        completed_job.status = 'completed'
        completed_job.save()

        # ---------- Bids ----------
        for job in jobs[:6]:   # half of jobs get bids
            if job.status == 'open' or job.status == 'in_progress':
                bidders = random.sample(freelancers, k=random.randint(1, 3))
                for freelancer in bidders:
                    Bid.objects.create(
                        job=job,
                        freelancer=freelancer,
                        amount=Decimal(random.randint(300, 2000)),
                        proposal=f'I can deliver this with excellence. My approach involves ...',
                        status='pending',
                    )

        # Accept a bid on the in_progress job
        if in_progress_job.bids.exists():
            accepted_bid = in_progress_job.bids.first()
            accepted_bid.status = 'accepted'
            accepted_bid.save()

        # ---------- Reviews ----------
        # Review on completed job
        if completed_job.status == 'completed':
            reviewer = completed_job.client
            reviewee = freelancers[0]  # assume first freelancer did the job
            Review.objects.create(
                job=completed_job,
                reviewer=reviewer,
                reviewee=reviewee,
                rating=5,
                comment='Excellent work, delivered ahead of schedule!',
            )

        # ---------- Services (freelancer offerings) ----------
        service_titles = [
            'Python Backend Development',
            'Custom API Development',
            'Modern UI/UX Design',
            'Technical Documentation',
            'Data Analysis & Reporting',
        ]
        for freelancer in freelancers:
            Service.objects.create(
                freelancer=freelancer,
                title=random.choice(service_titles),
                description=f'Professional {random.choice(service_titles)} service.',
                price=Decimal(random.choice([50, 100, 150])),
                category=random.choice(['web_dev', 'ui_ux', 'data_science', 'writing']),
            )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))