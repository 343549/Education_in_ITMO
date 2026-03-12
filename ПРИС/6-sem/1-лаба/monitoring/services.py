from datetime import timedelta

from django.utils import timezone

from .models import Measurement, Alert, Region


def generate_region_risk_analysis(region: Region) -> str:
    """
    Упрощённый модуль анализа риска.
    В реальном сервисе здесь можно вызывать внешнее LLM API.
    """
    now = timezone.now()
    since = now - timedelta(hours=24)

    measurements = Measurement.objects.filter(region=region, timestamp__gte=since)
    if not measurements.exists():
        return "Недостаточно данных за последние 24 часа для анализа рисков."

    count = measurements.count()
    avg_value = sum(m.value for m in measurements) / count

    if avg_value < 50:
        level = 'LOW'
        text_level = 'низкий'
    elif avg_value < 100:
        level = 'MEDIUM'
        text_level = 'средний'
    elif avg_value < 150:
        level = 'HIGH'
        text_level = 'высокий'
    else:
        level = 'CRITICAL'
        text_level = 'критический'

    Alert.objects.create(
        region=region,
        risk_level=level,
        message=(
            f"Среднее значение показателей за последние 24 часа составило {avg_value:.1f}. "
            f"Прогнозируемый уровень экологического риска: {text_level}."
        ),
        is_active=True,
    )

    return (
        f"Для региона «{region.name}» проанализированы данные за последние 24 часа.\n"
        f"Среднее значение показателей: {avg_value:.1f}.\n"
        f"Предварительный вывод: уровень экологического риска — {text_level}."
    )

