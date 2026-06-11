import requests

def send_email(api_key, receiver_email, form_link):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": "onboarding@resend.dev",
        "to": [receiver_email],
        "subject": "Please Fill Form",
        "html": f"""
        <h3>Form Request</h3>
        <p>Please fill the form:</p>
        <a href="{form_link}">
        {form_link}
        </a>
        """
    }

    response = requests.post(
        "https://api.resend.com/emails",
        headers=headers,
        json=payload
    )

    return response.status_code in [200, 201]
