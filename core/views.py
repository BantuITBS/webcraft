from django.shortcuts import render

def home(request):
    return render(request, 'core/index.html')
    

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json

@require_POST
@csrf_exempt  # Note: In production, implement proper CSRF protection
def submit_features(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)

        # Extract and validate required fields
        user_name = data.get('userName', '').strip()
        user_email = data.get('userEmail', '').strip()
        user_phone = data.get('userPhone', '').strip()
        budget_range = data.get('budgetRange', '').strip()
        selected_features = data.get('selectedFeatures', [])

        # Basic validation
        if not user_name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        if not user_email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        if not budget_range:
            return JsonResponse({'error': 'Budget range is required'}, status=400)
        if not selected_features:
            return JsonResponse({'error': 'At least one feature must be selected'}, status=400)

        # Format email content
        subject = f"New Website Feature Request from {user_name}"
        body = f"Client: {user_name}\n"
        body += f"Email: {user_email}\n"
        body += f"Phone: {user_phone or 'Not provided'}\n\n"
        body += f"Budget Range: {budget_range}\n\n"
        body += "Selected Features:\n"
        for index, feature in enumerate(selected_features, 1):
            body += f"{index}. {feature.get('category', 'Unknown')}: {feature.get('name', 'Unknown')} - {feature.get('description', 'No description')}\n"

        # Send email
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SUPPORT_EMAIL],  # Define SUPPORT_EMAIL in settings
            fail_silently=False,
        )

        # Return success response
        return JsonResponse({
            'message': 'Thank you! Your selections have been sent to our team. We will contact you soon to discuss your project.'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format'}, status=400)
    except Exception as e:
        # Log error in production
        return JsonResponse({'error': 'An error occurred while processing your request'}, status=500)
    
