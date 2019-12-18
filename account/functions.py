from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from django.conf import settings
from django.core.mail import send_mail


def encode_verification(user_id, salt):
    """
        generate an encrypted string containing a user_id
        use the 'salt' argument to namespace the verification strings
        for example, using 'verify_email' or 'reset_password'
        return the signed string
    """
    signer = URLSafeTimedSerializer(settings.SECRET_KEY, salt=salt)
    return signer.dumps(str(user_id))


def decode_verification(verification_string, salt, ttl=86400):
    """
        decode an encrypted string containing a user id
        use the 'salt' argument to namespace the verification strings
        use 'ttl' to enforce an expiration time on the signed string
        return the decoded user_id
    """
    try:
        signer = URLSafeTimedSerializer(settings.SECRET_KEY, salt=salt)
        user_id = signer.loads(verification_string, ttl)
        return user_id
    except (SignatureExpired, BadSignature):
        return None


VERIFY_EMAIL_SUBJECT = 'verify your email address'

VERIFY_EMAIL_BODY = '''
Please verify your email address.
In production, this should link to page that can handle the POST of this value.
{verification_string}
'''

def send_verify_email(email_address, verification_string):
    return send_mail(
        VERIFY_EMAIL_SUBJECT,
        VERIFY_EMAIL_BODY.format(verification_string=verification_string),
        settings.AUTH_EMAIL_FROM_ADDRESS,
        [email_address],
        fail_silently=False,
    )


RESET_EMAIL_SUBJECT = 'reset your password'

RESET_EMAIL_BODY = '''
Proceed to reset your password.
In production, this should link to page that can handle the password reset.
{verification_string}
'''

def send_reset_email(email_address, verification_string):
    return send_mail(
        RESET_EMAIL_SUBJECT,
        RESET_EMAIL_BODY.format(verification_string=verification_string),
        settings.AUTH_EMAIL_FROM_ADDRESS,
        [email_address],
        fail_silently=False,
    )


# nb: verification codes can't be utilized without a UI to handle link from email -> POST w/ code
