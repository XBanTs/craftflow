# marketplace/utils.py
from django.db.models import Avg, Count
from .models import Review


def get_client_ratings(jobs_queryset):
    """
    Returns two dicts: {client_id: avg_rating} and {client_id: review_count}
    for all unique clients in the given jobs queryset.

    Works safely on both sliced (e.g., [:6]) and unsliced querysets.
    """
    # Force evaluation and get unique client IDs using Python set()
    # (avoids calling .distinct() on a potentially sliced queryset)
    client_ids = set(jobs_queryset.values_list('client_id', flat=True))

    if not client_ids:
        return {}, {}

    reviews = (
        Review.objects
        .filter(reviewee_id__in=client_ids)
        .values('reviewee_id')
        .annotate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
        )
    )

    ratings_dict = {}
    counts_dict = {}
    for entry in reviews:
        uid = entry['reviewee_id']
        ratings_dict[uid] = round(entry['avg_rating'], 1)
        counts_dict[uid] = entry['total_reviews']

    return ratings_dict, counts_dict