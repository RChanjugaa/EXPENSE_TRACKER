from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ExpenseGroup, GroupMembership


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

# Create your tests here.
