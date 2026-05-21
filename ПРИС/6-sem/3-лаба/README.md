# Архитектурный проект микросервисной ИС EcoGuardian

**Студент:** Джафари Хоссаин  
**Группа:** К3340  
**Вариант:** 2  
**Предметная область:** интеллектуальный мониторинг экологической обстановки, прогноз рисков и оперативное реагирование (EcoGuardian).

> **Примечание по заданию:** в формулировке лабораторной требуется **архитектурный проект** (описание и диаграммы), а не обязательная реализация кода. Прототип Django из первой лабораторной работы в данном отчёте **не разрабатывается**; при необходимости на защите его можно упомянуть отдельно как учебный монолитный MVP.

**Диаграммы:** `diagrams/*.png` (исходники PlantUML — `diagrams/*.puml`).

---

## 1. Архитектурное видение и контекст

### 1.1. Цели системы и архитектуры

**Бизнес-цели**

| Цель | Описание |
|------|----------|
| Раннее выявление угроз | Снижение времени от отклонения показателей до оповещения ответственных служб |
| Обоснованное прогнозирование | Прогноз вероятности пожаров, наводнений, загрязнения воздуха по регионам |
| Координация реагирования | Учёт инцидентов, планов эвакуации и мероприятий по снижению последствий |
| Прозрачность для Минэкологии | Передача событий и отчётов во внешнюю ИС ведомства |

**Ключевые сценарии**

1. Непрерывный приём телеметрии с сети датчиков и валидация качества измерений.
2. Потоковый анализ и построение `RiskForecast` по региону по запросу оператора или по расписанию.
3. Формирование `Alert`, рассылка получателям (`AlertRecipient`), интеграция с SMS/e-mail.
4. Эскалация критического оповещения в `Incident` с планом эвакуации и мероприятиями.
5. Предоставление аналитикам Минэкологии доступа к прогнозам и отчётам.

**Целевые метрики (эксплуатационный профиль)**

| Метрика | Значение | Комментарий |
|---------|----------|-------------|
| Регионы мониторинга | 10 | Пилотный контур |
| Станции / датчики | ~50 станций, **500 датчиков** | ~10 датчиков на станцию |
| Поток измерений | **~1,7 RPS** ср., **до 15 RPS** пик | 1 замер / 5 мин на датчик |
| API операторов | **до 50 RPS** пик | 30 одновременных сессий |
| Время ответа прогноза | **≤ 5 с** (p95) | Согласовано с ТЗ модуля аналитики |
| Доступность | **99,9%** / месяц | ~43 мин простоя |
| Частота релизов | 1 релиз / 2 недели | Canary на stage, blue-green на prod |

### 1.2. Архитектурные драйверы

| Драйвер | Приоритет | Обоснование |
|---------|-----------|-------------|
| Масштабируемость потока данных | Высокий | Рост числа датчиков без остановки приёма |
| Надёжность и отказоустойчивость | Высокий | Экологические инциденты не терпят потери событий |
| Безопасность и разграничение доступа | Высокий | Данные госсектора, роли оператор / аналитик / реагирование |
| Интегрируемость | Средний | Минэкологии, метеослужба, SMS-шлюз |
| Сопровождаемость / скорость изменений | Средний | Независимые релизы сервисов |
| Наблюдаемость | Средний | Расследование задержек прогноза и доставки оповещений |
| Стоимость владения (учебный проект) | Средний | Docker Compose на одной VM вместо полного K8s на старте |

### 1.3. Контекстная диаграмма (System Context)

<img width="844" height="737" alt="image" src="https://github.com/user-attachments/assets/4318e83b-6d4d-4faf-aaf1-7eab2ad165d7" />


**Описание.** Система EcoGuardian находится в центре экосистемы: слева — поток данных от IoT-датчиков; справа — интеграция с **ИС Минэкологии** (отчёты, справочники), каналом SMS/e-mail и опционально метеослужбой. Пользователи: оператор регионального ЦУР, аналитик ведомства, специалист по реагированию. Все взаимодействия с UI идут через единую точку входа (API Gateway).

**Микрорефлексия.** Контекстная диаграмма зафиксировала границу системы и внешних зависимостей до декомпозиции на сервисы. Новым для себя отметил явное выделение **ACL оповещений** как внешней системы — это упрощает смену SMS-провайдера без переписывания домена оповещений.

---

## 2. Логическая архитектура и доменное моделирование

### 2.1. Доменные области и bounded contexts

| Bounded context | Ответственность | Связь с ER (lab2) |
|-----------------|-----------------|-------------------|
| **Catalog & Assets** | Регионы, станции, датчики, статусы оборудования | Region, MonitoringStation, Sensor |
| **Telemetry** | Приём, нормализация, хранение и выдача измерений | Measurement |
| **Risk Analytics** | Аномалии, прогнозы риска, версии ML-моделей | RiskForecast |
| **Alerting** | Оповещения, получатели, статусы доставки | Alert, AlertRecipient |
| **Incident Response** | Инциденты, эвакуация, мероприятия | Incident, EvacuationPlan, MitigationAction |
| **Identity & Access** | Пользователи ведомства, роли, аутентификация | AgencyUser |

Контексты **Alerting** и **Incident Response** связаны через событие эскалации; **Telemetry** и **Risk Analytics** — через read-модель агрегатов (API + Kafka).

### 2.2. Доменные модели (ключевые агрегаты)

**Catalog** — доменная модель каталога и телеметрии:
<img width="442" height="899" alt="image" src="https://github.com/user-attachments/assets/0e9afe3b-8051-4e3c-8711-2c300e45601e" />


**Risk Analytics**

| Элемент | Тип | Инварианты |
|---------|-----|------------|
| `RiskForecast` | Aggregate Root | `confidence ∈ [0,1]`; `riskLevel` из справочника; привязан к одному `regionId` |
| `ModelVersion` | Entity | Не более одной *production*-версии на тип риска |

**Alerting**

| Элемент | Тип | Инварианты |
|---------|-----|------------|
| `Alert` | Aggregate Root | Создаётся только при наличии `forecastId`; `severity` монотонно не снижается без явной команды |
| `AlertRecipient` | Entity | Уникальная пара (`alertId`, `userId`) |

**Incident Response**

| Элемент | Тип | Инварианты |
|---------|-----|------------|
| `Incident` | Aggregate Root | Один активный инцидент того же типа на регион (бизнес-правило пилота) |
| `EvacuationPlan` | Entity | Требует `approvedBy` для статуса *approved* |
| `MitigationAction` | Entity | `deadlineAt ≥ startedAt` инцидента |

### 2.3. Междоменные взаимодействия

**Доменные события (основные)**

| Событие | Издатель | Потребители | Смысл |
|---------|----------|-------------|-------|
| `measurement.received` | ingestion-service | telemetry-service | Сырое измерение принято |
| `measurement.stored` | telemetry-service | analytics-service | Данные доступны для анализа |
| `forecast.created` | analytics-service | alerting-service | Готов прогноз риска |
| `alert.created` | alerting-service | incident-service (опц.), audit | Сформировано оповещение |
| `alert.escalated` | alerting-service / API | incident-service | Эскалация в инцидент |
| `incident.opened` | incident-service | Минэкологии (ACL) | Начато реагирование |

**Процесс 1: «Прогноз → оповещение»** — оператор инициирует анализ; analytics публикует `forecast.created`; alerting создаёт Alert и инициирует доставку.
<img width="1343" height="640" alt="image" src="https://github.com/user-attachments/assets/9360c201-d4bc-4f62-9e6b-bf39e5d5bca7" />

**Процесс 2: «Оповещение → инцидент»** — команда `EscalateAlert`; incident-service создаёт Incident, связывает с Alert и Region; далее внутри агрегата добавляются EvacuationPlan и MitigationAction.

**Микрорефлексия.** Разбиение на шесть контекстов совпало с сущностями ER из второй лабораторной, что упростило трассировку требований. Понял, что **Incident** логичнее отделять от **Alert**: оповещение — сигнал, инцидент — управляемый жизненный цикл с планами.

---

## 3. Архитектура микросервисов

### 3.1. Состав микросервисов

Выбрано **8 сервисов** — достаточно для демонстрации распределённой архитектуры без избыточной дробности.

| Сервис | Домен | Ответственность | Основные операции | Владеемые данные |
|--------|-------|-----------------|-------------------|------------------|
| **api-gateway** | Cross-cutting | Маршрутизация, JWT, rate limit, TLS | Proxy, auth check | — (stateless) |
| **identity-service** | Identity & Access | Пользователи, роли, выдача JWT | login, refresh, CRUD users | AgencyUser, роли |
| **catalog-service** | Catalog | Справочник инфраструктуры | CRUD regions/stations/sensors | Region, MonitoringStation, Sensor |
| **ingestion-service** | Telemetry | Приём потока с датчиков | POST measurement batch | буфер → Kafka |
| **telemetry-service** | Telemetry | Запись и чтение рядов | query range, consume Kafka | Measurement (TimescaleDB) |
| **analytics-service** | Risk Analytics | Аномалии, прогноз | analyze region, schedule job | RiskForecast, ModelVersion |
| **alerting-service** | Alerting | Оповещения и доставка | create alert, list, escalate | Alert, AlertRecipient |
| **incident-service** | Incident Response | Инциденты и планы | open incident, plans, actions | Incident, EvacuationPlan, MitigationAction |

### 3.2. Диаграмма взаимодействия сервисов
<img width="1922" height="984" alt="image" src="https://github.com/user-attachments/assets/08a98307-5843-4aa1-993d-f6d094cb6021" />

**Синхронные связи:** клиент → api-gateway → сервисы (REST/JSON). analytics-service → telemetry-service (агрегаты за окно времени). alerting-service → внешний SMS через ACL.

**Асинхронные связи:** Kafka-топики между ingestion, telemetry, analytics, alerting, incident.

### 3.3. Анализ границ сервисов

**Почему так**

- **ingestion** отделён от **telemetry**: разная нагрузка (burst write vs query) и разное хранилище (TimescaleDB).
- **analytics** изолирован: тяжёлые CPU/GPU задачи и версии моделей не блокируют приём данных.
- **alerting** и **incident** разделены по жизненному циклу (сигнал vs операционное управление).

**Альтернативы**

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| Монолит (как в lab1) | Простота | Плохо масштабирует поток датчиков, связный релиз |
| 3 крупных сервиса | Меньше DevOps | Слабая изоляция ML и телеметрии |
| 15+ мелких сервисов | Максимальная изоляция | Высокая стоимость сети, Saga, наблюдаемости |

**Риски:** (1) распределённая транзакция «прогноз + оповещение» — решается Saga и идемпотентностью; (2) дублирование справочника регионов — read-only реплика или синхронный вызов catalog при создании Forecast.

**Микрорефлексия.** Восьмерка сервисов — компромисс между учебной полнотой и защитой на экзамене. Осознал, что граница режется по **изменяемости** (ML меняется часто) и по **паттерну нагрузки** (write-heavy telemetry).

---

## 4. Архитектура данных и согласованности

### 4.1. Модель владения данными

| Сервис | Сущности | Хранилище | Аргументация |
|--------|----------|-----------|--------------|
| catalog-service | Region, Station, Sensor | PostgreSQL | Реляционные связи, ACID |
| identity-service | AgencyUser | PostgreSQL (схема `identity`) | Транзакционная целостность |
| telemetry-service | Measurement | **TimescaleDB** | Временные ряды, компрессия, retention |
| analytics-service | RiskForecast, ModelVersion | PostgreSQL + **Yandex Object Storage** | Метаданные в SQL, артефакты моделей в S3 |
| alerting-service | Alert, AlertRecipient | PostgreSQL | Транзакции, отчёты |
| incident-service | Incident, Plan, Action | PostgreSQL | Связные агрегаты, FK внутри сервиса |
| ingestion-service | — | Kafka (временно) | Не владеет долговременными данными |

**Принцип:** один владелец — одна схема БД; межсервисный доступ только через API или события, без общих таблиц.

### 4.2. Межсервисная согласованность

**Паттерн 1: Saga (хореография) «Прогноз → оповещение»**

1. analytics-service сохраняет Forecast, публикует `forecast.created`.
2. alerting-service создаёт Alert; при сбое доставки SMS — компенсирующее событие `alert.delivery_failed`, повтор через outbox.
3. Согласованность **eventual**: Alert может появиться через 1–3 с после Forecast.

**Паттерн 2: Команда + событие «Эскалация в инцидент»**

- Синхронный POST `/alerts/{id}/escalate` в incident-service (идемпотентный ключ `Idempotency-Key`).
- incident-service проверяет статус Alert через API alerting (anti-corruption: DTO без внутренних полей).
- При успехе — `incident.opened` в Kafka для отчёта в Минэкологии.

**Идемпотентность:** ingestion и escalate принимают клиентский UUID; повтор не создаёт дубликат.

### 4.3. Эволюция и миграция данных

| Аспект | Подход |
|--------|--------|
| Версионирование схем | Flyway/Liquibase per service; только additive changes в API |
| Совместимость событий | Schema Registry (Avro/JSON Schema), поля optional |
| Миграция из монолита | *Опциональный сценарий*, не часть lab1: (1) выгрузка SQLite → CSV; (2) загрузка catalog + telemetry; (3) strangler-fig — новый ingestion, старый UI через gateway |
| Retention измерений | Hot 90 дней в TimescaleDB, cold archive в Object Storage |

**Микрорефлексия.** Разделение PostgreSQL и TimescaleDB стало главным архитектурным решением для потока 500 датчиков. Saga без оркестратора проще для учебного проекта, но потребует дисциплины в идемпотентности — это осознанный trade-off.

---

## 5. Архитектура API и интеграций

### 5.1. Внешний API системы

**API Gateway** — единая точка `https://api.ecoguardian.example.ru`, TLS 1.2+, JWT в заголовке `Authorization: Bearer`.

| Группа | Примеры | Версия |
|--------|---------|--------|
| Public operator API | `/api/v1/regions`, `/api/v1/alerts` | URL prefix `v1` |
| Ingestion API | `/api/v1/ingest/measurements` | отдельный rate limit, API-key датчиков |
| Admin | `/api/v1/admin/models` | роль `analyst` |

**Версионирование:** major в URL; minor — обратно совместимые поля JSON; deprecation 6 месяцев.

### 5.2. Межсервисные контракты (примеры)

#### Контракт 1: Приём измерений (ingestion-service)

```http
POST /api/v1/ingest/measurements
Content-Type: application/json
X-Api-Key: {sensorNetworkKey}
Idempotency-Key: {uuid}
```

```json
{
  "sensorId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "measuredAt": "2026-05-21T10:15:00Z",
  "value": 42.7,
  "qualityFlag": "OK"
}
```

**Ответ:** `202 Accepted` + `{ "measurementId": "...", "status": "queued" }`.  
**Идемпотентность:** повтор с тем же `Idempotency-Key` возвращает тот же `measurementId`.

#### Контракт 2: Запуск анализа (analytics-service, через gateway)

```http
POST /api/v1/regions/{regionId}/analyze
Authorization: Bearer {jwt}
```

```json
{ "windowHours": 24, "riskTypes": ["wildfire", "flood"] }
```

**Ответ:** `200` + тело Forecast или `202` + `jobId` при асинхронном режиме. SLA: p95 ≤ 5 с для синхронного режима на пилотных объёмах.

#### Контракт 3: Эскалация оповещения (incident-service)

```http
POST /api/v1/alerts/{alertId}/escalate
Idempotency-Key: {uuid}
```

```json
{
  "incidentType": "wildfire",
  "summary": "Критический уровень PM2.5, подтверждено оператором"
}
```

**Kafka `forecast.created` (фрагмент):**

```json
{
  "eventId": "uuid",
  "forecastId": "uuid",
  "regionId": "uuid",
  "riskType": "wildfire",
  "riskLevel": "HIGH",
  "confidence": 0.91,
  "occurredAt": "2026-05-21T10:20:00Z"
}
```

#### OpenAPI (фрагмент, ingestion)

```yaml
openapi: 3.0.3
info:
  title: EcoGuardian Ingestion API
  version: 1.0.0
paths:
  /api/v1/ingest/measurements:
    post:
      operationId: ingestMeasurement
      parameters:
        - in: header
          name: Idempotency-Key
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MeasurementIngest'
      responses:
        '202':
          description: Accepted
components:
  schemas:
    MeasurementIngest:
      type: object
      required: [sensorId, measuredAt, value]
      properties:
        sensorId: { type: string, format: uuid }
        measuredAt: { type: string, format: date-time }
        value: { type: number }
        qualityFlag: { type: string, enum: [OK, SUSPECT, INVALID] }
```

#### OpenAPI (фрагмент, analytics)

```yaml
paths:
  /api/v1/regions/{regionId}/analyze:
    post:
      operationId: analyzeRegion
      parameters:
        - name: regionId
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: Forecast ready
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RiskForecastDto'
```

### 5.3. Интеграции с внешними системами

| Система | Способ | Паттерн |
|---------|--------|---------|
| **ИС Минэкологии** | REST + nightly JSON-отчёты в SFTP | **Anti-Corruption Layer** (`minek-adapter`): внутренние DTO → формат ведомства |
| IoT-датчики | HTTPS / MQTT → ingestion | API-key, валидация по catalog |
| SMS/e-mail | REST провайдера | ACL в alerting-service, retry + circuit breaker |
| Метеослужба | REST (опционально) | Кэш 15 мин в Redis |

**Микрорефлексия.** Совмещение таблиц эндпоинтов и YAML OpenAPI помогает связать раздел API с реализацией на защите. ACL для Минэкологии — сознательная изоляция от «чужой» модели отчётности.

---

## 6. Качественные атрибуты и кросс-сервисные решения

### 6.1. Масштабируемость и производительность

| Компонент | Масштабирование | Узкое место / митигация |
|-----------|-----------------|-------------------------|
| ingestion, telemetry | Горизонтально (N реплик) | Kafka partitions = 12; ключ `sensorId` |
| analytics | 2–4 реплики, очередь задач | ML-инференс → async job + кэш Forecast |
| PostgreSQL | Вертикально → Managed PG | Индексы по `regionId`, read replica |
| TimescaleDB | Retention + continuous aggregates | Партиции по времени |

Кэш Redis: справочник регионов (TTL 5 мин), последний Forecast по региону.

### 6.2. Надёжность и отказоустойчивость

| Паттерн | Применение |
|---------|------------|
| Timeout | 2 с между сервисами, 5 с на ML |
| Retry | Экспоненциальный backoff, max 3 (идемпотентные GET/ingest) |
| Circuit Breaker | Вызов SMS-шлюза и Минэкологии |
| Fallback | При недоступности ML — эвристика по порогам (degraded mode) |
| Outbox | Публикация в Kafka в той же транзакции, что запись Alert |
| Dead Letter Queue | `*.dlq` для poison messages |

### 6.3. Безопасность

| Аспект | Решение |
|--------|---------|
| Аутентификация | **Упрощённый JWT** (HS256, access 15 мин, refresh 7 дней) от identity-service |
| Авторизация | RBAC: `operator`, `analyst`, `responder`, `admin`; проверка в gateway + повтор в сервисе |
| Транспорт | TLS везде; mTLS между сервисами — целевое улучшение prod |
| Секреты | Yandex Lockbox / env в Compose (учебный) |
| Датчики | Отдельный API-key, без JWT |

### 6.4. Наблюдаемость

| Сигнал | Инструмент | Назначение |
|--------|------------|------------|
| Логи | JSON → stdout, Loki (опц.) | Корреляция по `traceId` |
| Метрики | Prometheus | RPS, lag Kafka, latency p95, error rate |
| Трейсы | OpenTelemetry → Jaeger | Цепочка analyze → alert |
| Алерты | Grafana | Lag > 1000, 5xx > 1%, disk > 80% |

**Бизнес-метрики:** время `measurement.received` → `alert.created`, доля доставленных AlertRecipient.

**Микрорефлексия.** Деградация ML-режима — важный приём для госсистемы: лучше простой прогноз, чем полный отказ. Понял разницу между инфраструктурными и **бизнес-SLA** метриками.

---

## 7. Инфраструктурная архитектура и CI/CD

### 7.1. Целевая платформа

| Решение | Выбор | Обоснование |
|---------|-------|-------------|
| Облако | **Yandex Cloud** | Требование, российская юрисдикция данных |
| Контейнеризация | Docker | Единый артефакт сервисов |
| Оркестрация (учебный) | **Docker Compose** на VM 8 vCPU / 32 GB | Достаточно для пилота; ниже порог входа |
| Оркестрация (целевой prod) | Yandex Managed Kubernetes | Когда > 3 команд и нужен autoscaling |
| Брокер | **Apache Kafka** | Поток измерений и доменные события |
| CI | GitLab CI / GitHub Actions | Сборка, тесты, push в Container Registry |

### 7.1.1. Диаграмма развёртывания
<img width="1936" height="658" alt="image" src="https://github.com/user-attachments/assets/9a2a0302-756b-42b2-8bee-293412fc1395" />


### 7.2. Архитектура окружений

| Окружение | Назначение | Особенности |
|-----------|------------|-------------|
| **dev** | Разработка | Compose на локальной машине, embedded Kafka |
| **test** | Автотесты | CI поднимает Compose, Testcontainers |
| **stage** | Предпрод | VM в YC, anonymized data, canary |
| **prod** | Промышленный | Отдельный VPC, Managed PG/Kafka (этап 2) |

Изоляция: отдельные VPC/subnet, секреты, базы; повторяемость — Infrastructure as Code (Terraform для VM + Compose file).

### 7.3. CI/CD

```text
commit → lint/unit → build image → push registry
      → deploy test (Compose)
      → integration tests
      → deploy stage (canary 10% traffic 30 min)
      → manual approve → prod (blue-green)
```

| Практика | Описание |
|----------|----------|
| **Blue-green** | Prod: два слота Compose/stack, переключение upstream |
| **Canary** | Stage: 10% на новую версию analytics |
| Тесты | Unit ≥ 70% критичных модулей; contract-тесты Pact для ingestion↔telemetry; e2e сценарий «измерение → alert» |
| Rollback | Предыдущий тег image + миграции только additive |

**Микрорефлексия.** Docker Compose для учебного контура не противоречит целевому K8s: это ступень зрелости. На защите важно показать путь миграции на Managed-сервисы Yandex без смены границ микросервисов.

---

## Принятые архитектурные решения (для защиты)

1. **Yandex Cloud** — хостинг, Object Storage, опционально Managed Kafka/PostgreSQL.
2. **Docker Compose** на пилоте вместо K8s — снижение сложности; K8s как целевое развитие.
3. **Apache Kafka** — асинхронная шина между telemetry, analytics, alerting.
4. **Упрощённый JWT** — быстрый старт RBAC для ведомственных пользователей.
5. **Database-per-service** — PostgreSQL + TimescaleDB, без общей БД.

**Нагрузочный профиль:** 10 регионов, 500 датчиков, ~1,7 RPS ingest (пик 15), 50 RPS API.

---

## Приложение А. Промпты к БЯМ

Промпты вынесены отдельно — на защите показывать после основного содержания.

### А.1. Базовый промпт (контекст и сервисы)

```text
Ты — архитектор ПО. Спроектируй микросервисную архитектуру системы EcoGuardian
(вариант 2): мониторинг экологии, прогноз рисков (пожар, наводнение, загрязнение),
оповещения и реагирование (инциденты, эвакуация, мероприятия).

Ограничения: Yandex Cloud; Docker Compose для пилота; Kafka; JWT;
8 микросервисов максимум; 500 датчиков, 10 регионов, ~1.7 RPS ingest.
Внешние системы: IoT-датчики, ИС Минэкологии, SMS.

Выдай: (1) таблицу сервисов с владением данными; (2) список Kafka-событий;
(3) PlantUML C4 Context и Container; (4) риски границ сервисов.
Сущности из ER: Region, MonitoringStation, Sensor, Measurement, RiskForecast,
Alert, AgencyUser, AlertRecipient, Incident, EvacuationPlan, MitigationAction.
```

### А.2. Промпт: данные и Saga

```text
Для EcoGuardian опиши database-per-service: какие сущности в PostgreSQL,
какие в TimescaleDB, что в Object Storage. Для процессов «прогноз→оповещение»
и «эскалация в инцидент» предложи Saga (хореография или оркестрация),
идемпотентность и eventual consistency. Формат: таблицы + 10 предложений текста.
```

### А.3. Промпт: API и OpenAPI

```text
Сформируй 3 REST-контракта EcoGuardian: ingest measurement, analyze region,
escalate alert. Для каждого: метод, путь, заголовки (JWT, Idempotency-Key),
пример JSON, коды ответов. Добавь фрагмент OpenAPI 3.0 для ingest и analyze.
```

### А.4. Промпт: инфраструктура и CI/CD

```text
Опиши развёртывание EcoGuardian в Yandex Cloud на Docker Compose (8 vCPU, 32 GB):
состав контейнеров, dev/test/stage/prod, CI/CD с blue-green на prod и canary на stage.
Укажи Prometheus, Grafana, Jaeger. Когда переходить на Managed Kubernetes — критерии.
```

### А.5. Уточняющий промпт (после критики)

```text
Сократи до 8 микросервисов, объедини notification в alerting-service.
Добавь anti-corruption layer для Минэкологии. Укажи degraded mode при падении ML.
Верни только изменённые таблицы и 5 bullet рисков.
```

---

## Приложение Б. Исходники диаграмм

PNG в отчёте сгенерированы из PlantUML. Для пересборки:

```bash
cd lab3
plantuml diagrams/*.puml
```

---

## Итог

Подготовлен архитектурный проект микросервисной ИС **EcoGuardian** с 8 сервисами, событийной интеграцией через **Kafka**, раздельным хранением данных и внешним API через **Gateway**. Проект согласован с доменной моделью варианта 2 (включая подсистему реагирования из ER lab2), но не привязан к коду прототипа lab1. Диаграммы и промпты пригодны для защиты и доработки на следующих лабораторных.
