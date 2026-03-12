from django.contrib import admin
from .models import Region, Sensor, Measurement, Alert


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('region', 'sensor', 'metric_type', 'value', 'timestamp')
    list_filter = ('region', 'metric_type', 'timestamp')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('region', 'risk_level', 'is_active', 'created_at')
    list_filter = ('risk_level', 'is_active', 'created_at')
