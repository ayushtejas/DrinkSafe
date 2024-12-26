from django.db import models
import uuid
from django.core.validators import MinValueValidator

class Products(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True,editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10,decimal_places=2, validators=[MinValueValidator(0)])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering: ['-created']
        verbose_name = 'product'
        verbose_name_plural = 'products'