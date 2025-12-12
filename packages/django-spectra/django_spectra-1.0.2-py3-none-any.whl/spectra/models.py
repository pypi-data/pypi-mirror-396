from django.db import models
from django.core.cache import cache


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Django Spectra")
    logo = models.ImageField(upload_to='spectra/logos/', blank=True, null=True)
    logo_dark = models.ImageField(upload_to='spectra/logos/', blank=True, null=True)
    logo_sm = models.ImageField(upload_to='spectra/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='spectra/favicons/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        cache.delete('site_settings')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        settings = cache.get('site_settings')
        if not settings:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
            cache.set('site_settings', settings, 3600)
        return settings
