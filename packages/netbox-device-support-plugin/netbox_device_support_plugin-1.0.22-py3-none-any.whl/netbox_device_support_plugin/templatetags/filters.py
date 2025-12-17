from datetime import datetime, date
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


#### Helper Function #########################################################################################


def is_expired(value):
    """
    Helper Function
    """
    return value < datetime.now().date()


def expires_next_year(value):
    """
    Helper Function
    """
    return value < date(date.today().year + 1, 12, 31)


#### Django Template Filters #################################################################################


@register.filter(is_safe=True)
def expiration_class(value):
    """
    Set CSS class for date fields
    """
    if not value or value == "None" or value is None:
        return mark_safe('class="danger"')

    if is_expired(value):
        return mark_safe('class="danger"')
    elif expires_next_year(value):
        return mark_safe('class="warning"')


@register.filter(is_safe=True)
def coverage_class(value):
    """
    Set CSS class for text fields
    """
    if isinstance(value, str):
        if "Not covered" in value:
            return mark_safe('class="danger"')

    if not value or value == "None" or value is None:
        return mark_safe('class="danger"')


@register.filter(is_safe=True)
def coverage_class_boolian(value):
    """
    Set CSS class for boolian fields to display a green thick or a red cross
    """
    if isinstance(value, str):
        if "Not covered" in value:
            return mark_safe('class="mdi mdi-close-thick text-danger"')

    return (
        mark_safe('class="mdi mdi-check-bold text-success"')
        if value
        else mark_safe('class="mdi mdi-close-thick text-danger"')
    )


@register.filter(is_safe=True)
def contract_supplier_text(value):
    """
    Set CSS class for text fields
    """
    if isinstance(value, str):
        if "Not covered" in value:
            return mark_safe(value)

    return mark_safe(f"Covered by: {value}")


@register.filter(is_safe=True)
def eox_class(value):
    """
    Set CSS class for text fields
    """
    if value or value == "None" or value is None:
        return mark_safe('class="danger"')


@register.filter(is_safe=True)
def eox_class_boolian(value):
    """
    Set CSS class for boolian fields to display a green thick or a red cross
    """
    return (
        mark_safe('class="mdi mdi-close-thick text-danger"')
        if value
        else mark_safe('class="mdi mdi-check-bold text-success"')
    )


@register.filter(is_safe=True)
def desired_release_status_class(value):
    """
    Set CSS class for text fields
    """
    if not value or value == "None" or value is None:
        return mark_safe('class="warning"')


@register.filter(is_safe=True)
def current_release_status_class(value):
    """
    Set CSS class for text fields
    """
    if not value or value == "None" or value is None:
        return mark_safe('class="danger"')
