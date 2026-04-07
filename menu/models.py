from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name_plural = "Sub Categories"

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='food_items')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='food_items')
    image = models.ImageField(upload_to='food/')
    is_best_seller = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save to prevent re-uploading unchanged images to Cloudinary"""
        # If this is an existing object, check if the image has actually changed
        if self.pk:
            try:
                existing = FoodItem.objects.get(pk=self.pk)
                # If image hasn't changed, don't update it
                if existing.image == self.image:
                    # Exclude image from update_fields to prevent re-upload
                    if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                        kwargs['update_fields'] = tuple(f for f in kwargs['update_fields'] if f != 'image')
            except FoodItem.DoesNotExist:
                pass
        super().save(*args, **kwargs)
