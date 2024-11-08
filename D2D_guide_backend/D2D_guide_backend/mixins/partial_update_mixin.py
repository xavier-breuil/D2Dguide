class PartialUpdateMixin:
    """
    Enable partial update on views with action update.
    """
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)