from django.contrib import admin
from .models import Accolade, Organization, Outcome, Scope, AccoladeLike
# Register your models here.
admin.site.register(Accolade)
admin.site.register(Organization)
admin.site.register(Outcome)
admin.site.register(Scope)
admin.site.register(AccoladeLike)