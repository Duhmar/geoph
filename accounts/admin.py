from django.contrib import admin
from .models import Report, ReportMedia, Profile, Comment, Province, Accommodation, TouristSpot, TransportationTerminal

# Register your models here.
admin.site.register(Report)
admin.site.register(ReportMedia)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Province)
admin.site.register(Accommodation)
admin.site.register(TouristSpot)
admin.site.register(TransportationTerminal)