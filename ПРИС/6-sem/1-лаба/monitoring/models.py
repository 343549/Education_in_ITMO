from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Sensor(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    METRIC_TYPES = [
        ('AQI', 'Индекс качества воздуха'),
        ('TEMP', 'Температура'),
        ('HUM', 'Влажность'),
        ('CO2', 'CO₂'),
        ('OTHER', 'Другое'),
    ]

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=10, choices=METRIC_TYPES)
    value = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f'{self.region} {self.metric_type} {self.value} @ {self.timestamp}'


class Alert(models.Model):
    RISK_LEVELS = [
        ('LOW', 'Низкий'),
        ('MEDIUM', 'Средний'),
        ('HIGH', 'Высокий'),
        ('CRITICAL', 'Критический'),
    ]

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.region} [{self.get_risk_level_display()}]'
