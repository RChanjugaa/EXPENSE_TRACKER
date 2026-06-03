from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import ExpenseGroup, GroupInvitation, GroupMembership


class GroupAccessTests(TestCase):
    def test_user_only_sees_their_own_groups(self):
        User = get_user_model()
        user = User.objects.create_user(username='user', password='pass12345')
        other = User.objects.create_user(username='other', password='pass12345')
        own_group = ExpenseGroup.objects.create(name='Own', created_by=user)
        other_group = ExpenseGroup.objects.create(name='Other', created_by=other)
        GroupMembership.objects.create(group=own_group, user=user)
        GroupMembership.objects.create(group=other_group, user=other)

        self.client.login(username='user', password='pass12345')
        response = self.client.get(reverse('group_list'))

        self.assertContains(response, 'Own')
        self.assertNotContains(response, 'Other')


class GroupInvitationTests(TestCase):
    def test_group_admin_can_email_invitation_and_user_can_accept(self):
        User = get_user_model()
        admin = User.objects.create_user(username='admin', email='admin@gmail.com', password='pass12345')
        invited = User.objects.create_user(username='invited', email='invited@gmail.com', password='pass12345')
        group = ExpenseGroup.objects.create(name='Project Trip', created_by=admin)
        GroupMembership.objects.create(group=group, user=admin, role=GroupMembership.Role.ADMIN)

        self.client.login(username='admin', password='pass12345')
        response = self.client.post(reverse('invite_member', args=[group.pk]), {'email': 'invited@gmail.com'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Project Trip', mail.outbox[0].body)

        invitation = GroupInvitation.objects.get()
        self.client.logout()
        self.client.login(username='invited', password='pass12345')
        response = self.client.get(reverse('accept_group_invitation', args=[invitation.token]))

        self.assertEqual(response.status_code, 302)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, GroupInvitation.Status.ACCEPTED)
        self.assertTrue(GroupMembership.objects.filter(group=group, user=invited).exists())

# Create your tests here.

