from django.contrib import admin
from .models import Report, ReportMedia, Profile, Comment, Hotel, RoomBooking, Municipality, Accommodation, TouristSpot, TransportationTerminal

# Registering your existing models
admin.site.register(Report)
admin.site.register(ReportMedia)
admin.site.register(Profile)
admin.site.register(Comment)

admin.site.register(Hotel)
admin.site.register(RoomBooking)
admin.site.register(Municipality)
admin.site.register(Accommodation)
admin.site.register(TouristSpot)
admin.site.register(TransportationTerminal)