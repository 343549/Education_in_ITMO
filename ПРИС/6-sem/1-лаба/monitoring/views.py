from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Region, Alert
from .services import generate_region_risk_analysis


def index(request):
    regions = Region.objects.all()
    alerts = (
        Alert.objects.filter(is_active=True)
        .order_by('region', '-created_at')
    )
    alerts_by_region = {}
    for alert in alerts:
        if alert.region_id not in alerts_by_region:
            alerts_by_region[alert.region_id] = alert

    context = {
        'regions': regions,
        'alerts_by_region': alerts_by_region,
        'now': timezone.now(),
    }
    return render(request, 'index.html', context)


def region_detail(request, region_id):
    region = get_object_or_404(Region, pk=region_id)
    alerts = Alert.objects.filter(region=region).order_by('-created_at')[:10]

    context = {
        'region': region,
        'alerts': alerts,
    }
    return render(request, 'region_detail.html', context)


def analyze_region(request, region_id):
    region = get_object_or_404(Region, pk=region_id)
    generate_region_risk_analysis(region)
    return redirect('region_detail', region_id=region.id)
