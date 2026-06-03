from django import template

register = template.Library()


@register.filter
def currency(value):
    try:
        return f"R {float(value):,.2f}"
    except (TypeError, ValueError):
        return value


@register.filter
def status_badge(status):
    mapping = {
        'pending': 'status-pending',
        'paid': 'status-paid',
        'verified': 'status-verified',
        'rejected': 'status-rejected',
    }
    return mapping.get(status, 'text-bg-secondary')


@register.filter
def alert_class(tags):
    """Convert Django message tags to Bootstrap alert classes."""
    if not tags:
        return 'info'
    tag = tags.split()[-1]
    return 'danger' if tag == 'error' else tag
