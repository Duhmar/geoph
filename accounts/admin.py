from django.contrib import admin
from .models import Report, ReportMedia, Profile, Comment, Hotel, RoomBooking, Province, Accommodation, TouristSpot, TransportationTerminal

# Register your models here.
admin.site.register(Report)
admin.site.register(ReportMedia)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Hotel)
admin.site.register(RoomBooking)

# The new GeoPH models
admin.site.register(Province)
admin.site.register(Accommodation)
admin.site.register(TouristSpot)
admin.site.register(TransportationTerminal)