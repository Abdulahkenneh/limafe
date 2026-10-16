# limafi_site/management/commands/generate_templates.py
from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate all templates including base.html with SEO properties, and others inheriting from it'

    def handle(self, *args, **kwargs):
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        os.makedirs(templates_dir, exist_ok=True)

        # Create base.html with SEO meta tags
        base_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{% block meta_description %}Liberian Mandingo Living in Europe Association - Default Description{% endblock %}">
    <meta name="keywords" content="{% block meta_keywords %}LIMAFI, Liberian Mandingo, Europe, association, community{% endblock %}">
    <meta name="author" content="LIMAFI">
    <!-- OpenGraph for social sharing -->
    <meta property="og:title" content="{% block og_title %}LIMAFI{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Default OG Description{% endblock %}">
    <meta property="og:image" content="{% block og_image %}{% endblock %}">
    <meta property="og:url" content="{% block og_url %}{% endblock %}">
    <meta property="og:type" content="website">
    <title>{% block title %}LIMAFI{% endblock %}</title>
    {% block extra_head %}{% endblock %}
    <!-- Add CSS links or other head elements here -->
</head>
<body>
    <header>
        <!-- Common header: navigation, logo, etc. -->
        <nav>
            <!-- Navigation links -->
        </nav>
    </header>
    <main>
        {% block content %}
        {% endblock %}
    </main>
    <footer>
        <!-- Footer: copyright, links, etc. -->
        &copy; {% now "Y" %} LIMAFI Association
    </footer>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
"""
        base_path = os.path.join(templates_dir, 'base.html')
        if not os.path.exists(base_path):
            with open(base_path, 'w') as f:
                f.write(base_content)
            self.stdout.write(self.style.SUCCESS('Created base.html'))
        else:
            self.stdout.write(self.style.WARNING('base.html already exists, skipping'))

        # List of all template names from views
        template_names = [
            'signup.html', 'login.html', 'profile.html', 'user_update.html', 'password_reset.html',
            'page_list.html', 'page_detail.html', 'page_form.html',
            'post_list.html', 'post_detail.html', 'post_form.html',
            'project_list.html', 'project_detail.html', 'project_form.html',
            'media_form.html',
            'event_list.html', 'event_detail.html', 'event_form.html', 'booking_form.html',
            'donation_list.html', 'donation_form.html',
            'message_list.html', 'message_form.html',
            'newsletter_form.html', 'contact.html',
            'dashboard.html',
            # Add any additional templates if needed
        ]

        # Create each template inheriting from base.html
        for name in template_names:
            content = """
{% extends "base.html" %}

{% block title %}{{ block.super }} - """ + name.replace('.html', '').replace('_', ' ').title() + """{% endblock %}

{% block meta_description %}Description for """ + name.replace('.html', '').replace('_', ' ').title() + """ page on LIMAFI website.{% endblock %}

{% block meta_keywords %}Limafi, """ + name.replace('.html', '').replace('_', ', ') + """{% endblock %}

{% block content %}
    <h1>""" + name.replace('.html', '').replace('_', ' ').title() + """</h1>
    <!-- Add your content here -->
    {% if form %}
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit">Submit</button>
        </form>
    {% endif %}
    {% if object_list %}
        <ul>
            {% for obj in object_list %}
                <li>{{ obj }}</li>
            {% endfor %}
        </ul>
    {% elif object %}
        <p>{{ object }}</p>
    {% endif %}
{% endblock %}
"""
            template_path = os.path.join(templates_dir, name)
            if not os.path.exists(template_path):
                with open(template_path, 'w') as f:
                    f.write(content)
                self.stdout.write(self.style.SUCCESS(f'Created {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'{name} already exists, skipping'))

        self.stdout.write(self.style.SUCCESS('All templates generated successfully'))