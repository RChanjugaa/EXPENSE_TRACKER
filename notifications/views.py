from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render


@login_required
def notification_list(request):
    qs = request.user.notifications.all()
    unread_count = qs.filter(is_read=False).count()
    # Mark all as read when page is opened
    qs.filter(is_read=False).update(is_read=True)
    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'notifications/notification_list.html', {
        'notifications': page_obj,
        'page_obj': page_obj,
        'unread_count': unread_count,
    })


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notification_list')

# Create your views here.
