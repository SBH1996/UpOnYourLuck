import os
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from localflavor.us.models import USStateField
from PIL import Image
import os
from django.utils.deconstruct import deconstructible
from django.core.files.storage import FileSystemStorage

@deconstructible
class UploadToPathAndRename(object):

    def __init__(self, user, path):
        self.sub_path = path
        self.user = user

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        if instance.pk:
            filename = '{}.{}'.format(instance.user.username, ext)

        # return the whole path to the file
        return os.path.join(self.sub_path, filename)

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join('media', name))
        return name

def rename_profile_img(user, path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        if instance.pk:
            filename = '{}.{}'.format(instance.pk, ext)
        else:
            filename = '{}.{}'.format(user.username, ext)
        return os.path.join(path, filename)
    return wrapper

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_url = models.URLField(max_length=200)
    life_story = models.TextField(max_length=500)
    profile_img = models.ImageField(upload_to=UploadToPathAndRename(user, "profile_img/"), default='profile_img/default.jpg', storage=OverwriteStorage())
    qr_code_img = models.FilePathField(path='media/qr_code/')
    payment_link_url = models.URLField(max_length=200, default="https://cash.app/$")
    city = models.CharField(default="Raleigh", max_length=60)
    state = USStateField(default="NC", blank=True)

    class Meta:
        db_table = 'Profile'
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return str(self.user.username)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.profile_img.path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_img.path)

    def get_profile_url(self):
        return self.profile_url


# create a user profile automatically upon account creation using signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # set default values for profile url, and qr code img
        Profile.objects.create(
            user=instance, profile_url=instance.username,
        )