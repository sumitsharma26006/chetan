import json
from groq import Groq, APIError, AuthenticationError, RateLimitError
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.conf import settings
from django.template.loader import get_template, TemplateDoesNotExist

# Initialize Groq client once at module level
client = None
if getattr(settings, 'GROQ_API_KEY', None):
    client = Groq(api_key=settings.GROQ_API_KEY)

CRISIS_KEYWORDS = [
    'suicide', 'depressed', 'hurt', 'kill myself',
    'hopeless', 'end my life', 'harm myself', 'worthless'
]

@ensure_csrf_cookie
def home_view(request):
    """Safely renders index.html from any configured template directory pathway."""
    for template_path in ['index.html', 'chat/index.html']:
        try:
            get_template(template_path)
            return render(request, template_path)
        except TemplateDoesNotExist:
            continue
    raise Http404("index.html not found in any template directory")

@csrf_exempt
def send_message_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            user_mood = data.get('mood', 'neutral')

            if not user_message:
                return JsonResponse({'error': 'Message content is empty'}, status=400)

            # Limit message length to avoid token overuse
            user_message = user_message[:500]

            # Crisis trigger safeguard
            if any(word in user_message.lower() for word in CRISIS_KEYWORDS):
                return JsonResponse({
                    'reply': "🚨 Safety Alert: I noticed you might be going through a tough time. Please reach out to a trusted professional or emergency services. Help is available."
                })

            # Check if client was initialized (i.e. API key was present at startup)
            if client is None:
                return JsonResponse({'reply': "Error: GROQ_API_KEY missing in settings.py"})

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are a helpful, professional personal advisor. The user feels {user_mood}. "
                            "Acknowledge their feeling directly in 1 short sentence. "
                            "Then, provide exactly 3 actionable, punchy bullet points to help them. "
                            "Use simple, universal language and keep each point under 8 words."
                        )
                    },
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,
                max_tokens=150
            )

            if hasattr(completion, 'choices') and len(completion.choices) > 0:
                bot_reply = completion.choices[0].message.content
                return JsonResponse({'reply': bot_reply})
            else:
                return JsonResponse({'reply': f"Unexpected Groq response structure: {str(completion)}"})

        except AuthenticationError:
            return JsonResponse({'reply': "Error: Invalid GROQ API key. Check your settings.py."})
        except RateLimitError:
            return JsonResponse({'reply': "Rate limit reached. Please wait a moment and try again."})
        except APIError as e:
            return JsonResponse({'reply': f"Groq API error: {e.message}"})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'reply': f"Unexpected server error: {str(e)}"})

    return JsonResponse({'error': 'Method not allowed'}, status=405)