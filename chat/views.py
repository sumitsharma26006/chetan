import json
from groq import Groq
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.conf import settings
from django.template.loader import get_template, TemplateDoesNotExist

CRISIS_KEYWORDS = [
    'suicide', 'depressed', 'hurt', 'kill myself',
    'hopeless', 'end my life', 'harm myself', 'worthless'
]

def get_client():
    key = getattr(settings, 'GROQ_API_KEY', None)
    if key:
        return Groq(api_key=key)
    return None

@ensure_csrf_cookie
def home_view(request):
    for template_path in ['chat/index.html', 'index.html']:
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

            user_message = user_message[:500]

            if any(word in user_message.lower() for word in CRISIS_KEYWORDS):
                return JsonResponse({
                    'reply': "I hear you. You are not alone. Please talk to someone you trust or call a helpline. Help is always available. You matter. 💙"
                })

            client = get_client()
            if client is None:
                return JsonResponse({'reply': "Error: GROQ_API_KEY missing in settings.py"})

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are a kind and caring mental health companion named Chetan. The user feels {user_mood}. "
                            "Use very simple, easy words that anyone from age 4 to 80 can understand. No difficult words. "
                            "First, say 1 short sentence showing you understand their feeling. "
                            "Then give exactly 3 simple tips to help them feel better. "
                            "Each tip must be under 8 words. Be warm, friendly and easy to read."
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
                return JsonResponse({'reply': "Sorry, I could not get a response. Please try again."})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'reply': f"Something went wrong. Please try again."})

    return JsonResponse({'error': 'Method not allowed'}, status=405)