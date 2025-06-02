
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

# Organization Model
class Organization(models.Model):
    name = models.CharField(max_length=125)

    def __str__(self):
        return self.name

# Outcome Model
class Outcome(models.Model):
    title = models.CharField(max_length=125)
    score = models.CharField(max_length=125)

    def __str__(self):
        return f"{self.title} - {self.score}"

# Scope Model
class Scope(models.Model):
    scope = models.CharField(max_length=125)
    score = models.CharField(max_length=125)

    def __str__(self):
        return f"{self.scope} - {self.score}"

# Accolades (Post-like model)
class Accolade(models.Model):
    content = RichTextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    scope = models.ForeignKey(Scope, on_delete=models.CASCADE)
    skills = models.CharField(max_length=255)
    date = models.DateField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} - {self.outcome.title}"

# Like Model
class AccoladeLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accolade = models.ForeignKey(Accolade, on_delete=models.CASCADE, related_name='likes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'accolade')

    def __str__(self):
        return f"{self.user.username} liked {self.accolade}"