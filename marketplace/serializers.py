from rest_framework import serializers
from .models import Job, Bid, Service
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    A minimal, safe representation of a User for nested API responses.
    We never expose password, is_staff, or other internal fields.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        # Explicit whitelist: if the User model gains new fields later,
        # they won't accidentally leak to the API.


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for Job model.
    - client is nested (read_only because it's set by the view).
    - bid_count is a computed field.
    """
    client = UserSerializer(read_only=True)
    # read_only=True: the client is set in perform_create() from request.user,
    # never from incoming JSON. Also prevents impersonation.

    bid_count = serializers.SerializerMethodField()
    # SerializerMethodField: runs a method get_<field_name>() to compute a value.

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'budget', 'status',
            'category', 'client', 'bid_count', 'attachment',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
        # These are set by the system, not by API consumers.

    def get_bid_count(self, obj):
        """
        obj is the Job instance being serialized.
        Returns the number of bids on this job.
        """
        return obj.bids.count()


class BidSerializer(serializers.ModelSerializer):
    """
    Serializer for Bid model.
    Used when creating a bid via the API.
    """
    freelancer = UserSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'job', 'freelancer', 'amount', 'proposal', 'status', 'created_at']
        read_only_fields = ['id', 'freelancer', 'status', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model.
    """
    freelancer = UserSerializer(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'price', 'category', 'freelancer', 'created_at']
        read_only_fields = ['id', 'freelancer', 'created_at']