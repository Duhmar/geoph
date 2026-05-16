from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from datetime import date

class Report(models.Model):
    REGION_CHOICES = [
        ('Luzon', 'Luzon'),
        ('Visayas', 'Visayas'),
        ('Mindanao', 'Mindanao'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='Luzon')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_reports', blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)

    def __str__(self):
        return self.title

class ReportMedia(models.Model):
    report = models.ForeignKey(Report, related_name='additional_media', on_delete=models.CASCADE)
    file = models.FileField(upload_to='report_media/')
    is_video = models.BooleanField(default=False)    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    civil_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married'), ('Widowed', 'Widowed'), ('Divorced', 'Divorced')], blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
        except FileNotFoundError:
            pass
        
    @property
    def age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None    
    
class Comment(models.Model):
    report = models.ForeignKey(Report, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.report.title}'
    

class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Accommodation(models.Model):
    name = models.CharField(max_length=200)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='accommodations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_fully_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.province.name})"

class TouristSpot(models.Model):
    CATEGORY_CHOICES = [
        ('BEACH', 'Beach/Resort'),
        ('LAGOON', 'Lagoon/Pool'),
        ('ISLET', 'Islet/Island'),
        ('NATURE', 'Forest/Cave/Rock Formation'),
        ('HISTORICAL', 'Historical/Shrine'),
    ]

    name = models.CharField(max_length=200)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='tourist_spots', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='BEACH')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"

class TransportationTerminal(models.Model):
    TERMINAL_TYPES = [
        ('PORT', 'Seaport'),
        ('HABAL_HABAL', 'Habal-Habal Terminal'),
    ]
    
    name = models.CharField(max_length=200)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='transport_terminals', null=True, blank=True)
    terminal_type = models.CharField(max_length=20, choices=TERMINAL_TYPES, default='PORT')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_terminal_type_display()})"