from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .manager import invalidate

@receiver(post_save)
def on_save(sender, instance, **kwargs):
    try:
        pk = instance.pk
    except AttributeError:
        return
    # ignore Django migrations and proxies
    if getattr(sender._meta, 'proxy', False):
        return
    invalidate(sender, pk)

@receiver(post_delete)
def on_delete(sender, instance, **kwargs):
    try:
        pk = instance.pk
    except AttributeError:
        return
    if getattr(sender._meta, 'proxy', False):
        return
    invalidate(sender, pk)
