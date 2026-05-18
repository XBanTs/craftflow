from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Job, Bid, Service
from .serializers import JobSerializer, BidSerializer, ServiceSerializer


class JobListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/jobs/ → list all open jobs (public)
    POST /api/jobs/ → create a new job (authenticated required)
    """
    queryset = Job.objects.filter(status='open').order_by('-created_at').select_related('client')
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # IsAuthenticatedOrReadOnly: GET allowed for anyone,
    # POST requires authentication (session or basic auth).

    def perform_create(self, serializer):
        """
        Called after the serializer validates successfully.
        We inject the client (request.user) before saving.
        """
        serializer.save(client=self.request.user)


class JobDetailAPIView(generics.RetrieveDestroyAPIView):
    """
    GET /api/jobs/<pk>/ → job detail (public)
    DELETE /api/jobs/<pk>/ → delete a job (authenticated, owner only)
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_permissions(self):
        """
        Dynamic permissions: GET is public, DELETE requires authentication.
        """
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to add ownership check.
        Only the job's client can delete it.
        """
        job = self.get_object()
        if job.client != request.user:
            return Response(
                {'error': 'You do not have permission to delete this job.'},
                status=status.HTTP_403_FORBIDDEN
            )
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BidCreateAPIView(generics.CreateAPIView):
    """
    POST /api/bids/ → submit a bid on a job (authenticated)
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Inject the freelancer (request.user) before saving.
        """
        serializer.save(freelancer=self.request.user)


class ServiceListAPIView(generics.ListAPIView):
    """
    GET /api/services/ → list all services (public)
    """
    queryset = Service.objects.all().select_related('freelancer')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny()]


class ServiceDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/services/<pk>/ → service detail (public)
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny()]