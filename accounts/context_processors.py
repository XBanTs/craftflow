from .models import UserVerification

def verification_status(request):
    if request.user.is_authenticated:
        try:
            is_email_verified = request.user.verification.email_verified
        except UserVerification.DoesNotExist:
            is_email_verified = False
        return {'is_email_verified': is_email_verified}
    return {}