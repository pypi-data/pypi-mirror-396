from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    tenant = models.ForeignKey(Tenant, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Provider(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="providers")
    tenant = models.ForeignKey(Tenant, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Booking(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, null=True, blank=True, on_delete=models.SET_NULL)
    start = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default="confirmed")
    allow_cancel = models.BooleanField(default=True)
    allow_reschedule = models.BooleanField(default=True)
    tenant = models.ForeignKey(Tenant, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.reference

    def can_cancel(self):
        return self.allow_cancel

    def can_reschedule(self):
        return self.allow_reschedule
