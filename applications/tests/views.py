from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_date_extensions.fields import ApproximateDate

from core.models import Event, EventPage, User
from applications.models import Form, Application, Score
from applications.utils import DEFAULT_QUESTIONS
from applications.views import applications

class ApplyView(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.event = Event.objects.create(name='Test', city='Test', country='Test')
        self.page = EventPage.objects.create(event=self.event, is_live=True, url='test')
        self.form = Form.objects.create(page=self.page)

    def test_access_apply_view(self):
        resp = self.client.get(reverse('applications:apply', args=['test']))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form_obj'], self.form)
        self.assertEqual(len(resp.context['form'].fields), len(DEFAULT_QUESTIONS))

        # Redirect to event page because there is no form
        self.form.delete()
        resp = self.client.get(reverse('applications:apply', args=['test']))
        self.assertEqual(resp.status_code, 302)

        # Show 404 because there is no event page
        self.page.delete()
        resp = self.client.get(reverse('applications:apply', args=['test']))
        self.assertEqual(resp.status_code, 404)


class ApplicationsView(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.event = Event.objects.create(name='Test', city='Test', country='Test')
        self.page = EventPage.objects.create(event=self.event, is_live=True, url='test')
        self.form = Form.objects.create(page=self.page)
        self.form_2 = Form.objects.create(page=self.page)
        self.user = User.objects.create(email='test@user.com', is_active=True, is_staff=True)
        self.user.set_password('test')
        self.user_2 = User.objects.create(email='test2@user.com')

        self.application_1 = Application.objects.create(form=self.form, state='submitted')
        self.application_2 = Application.objects.create(form=self.form, state='accepted')
        self.application_3 = Application.objects.create(form=self.form, state='rejected')
        self.application_4 = Application.objects.create(form=self.form, state='waitlisted')

        self.url = reverse('applications:applications', args=['test'])

    def test_access_applications_view(self):
        # as anonymous user
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)

        # as logged in user, but not orgarniser of given event
        request = self.factory.get(self.url)
        request.user = self.user
        resp = applications(request, city='test')
        self.assertEqual(resp.status_code, 404)

        # as superuser
        self.user.is_superuser = True
        self.user.save()
        request = self.factory.get(self.url)
        request.user = self.user
        resp = applications(request, city='test')
        self.assertEqual(resp.status_code, 200)

        # as organiser of given event
        self.user.is_superuser = False
        self.user.save()
        self.event.team.add(self.user)
        self.event.save()
        request = self.factory.get(self.url)
        request.user = self.user
        resp = applications(request, city='test')
        self.assertEqual(resp.status_code, 200)

    def test_get_applications_list(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(email='test@user.com', password='test')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['applications']), 4)

        # change one application's form
        self.application_1.form = self.form_2
        self.application_1.save()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['applications']), 3)

    def test_get_sorted_applications_list(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(email='test@user.com', password='test')

        # Add some scores:
        Score.objects.create(application=self.application_1, user=self.user, score=2.0)
        Score.objects.create(application=self.application_1, user=self.user_2, score=4.0)
        Score.objects.create(application=self.application_2, user=self.user, score=3.0)
        Score.objects.create(application=self.application_2, user=self.user_2, score=3.0)
        Score.objects.create(application=self.application_3, user=self.user, score=3.0)
        Score.objects.create(application=self.application_3, user=self.user_2, score=4.0)

        # Order by average_score
        resp = self.client.get('{}?order=average_score'.format(self.url))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['applications']), 4)
        self.assertEqual(resp.context['applications'], [self.application_4, self.application_1, self.application_2, self.application_3])
        self.assertEqual(resp.context['order'], 'average_score')

        # Order by -average_score
        resp = self.client.get('{}?order=-average_score'.format(self.url))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['applications']), 4)
        self.assertEqual(resp.context['applications'], [self.application_3, self.application_2, self.application_1, self.application_4])
        self.assertEqual(resp.context['order'], '-average_score')

    def get_filtered_applications_list(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(email='test@user.com', password='test')

        # No filter
        resp = self.client.get(self.url)
        self.assertEqual(len(resp.context['applications']), 4)

        # Filter by submitted
        resp.self.client.get('{}?state=submitted'.format(self.url))
        self.assertEqual(len(resp.context['applications']), 1)
        self.assertEqual(resp.context['applications'], [self.application_1])

        # Filter by accepted
        resp.self.client.get('{}?state=accepted'.format(self.url))
        self.assertEqual(len(resp.context['applications']), 1)
        self.assertEqual(resp.context['applications'], [self.application_2])

        # Filter by rejected
        resp.self.client.get('{}?state=rejected'.format(self.url))
        self.assertEqual(len(resp.context['applications']), 1)
        self.assertEqual(resp.context['applications'], [self.application_3])

        # Filter by wait listed
        resp.self.client.get('{}?state=waitlisted'.format(self.url))
        self.assertEqual(len(resp.context['applications']), 1)
        self.assertEqual(resp.context['applications'], [self.application_4])
