# django-providers

Reusable Django app for modelling service providers and resources in booking systems.

## Overview

`django-providers` models who or what can deliver a service within a booking ecosystem. It introduces a dedicated providers layer so that services, availability, and booking flows can treat providers as first-class objects rather than ad-hoc foreign keys. The design mirrors SimplyBook-style separation without claiming feature parity; it focuses solely on representing providers and their capability to deliver services.

## Scope

### What this app provides
- Provider and resource models with common metadata (name, provider_type, visibility, ordering)
- Mapping between services and the providers/resources that can deliver them
- Reusable abstractions for distinguishing people and physical resources while sharing behaviour
- Optional multi-tenancy support without enforcing a tenancy framework

### What this app does NOT provide
- Availability schedules or calendars
- Slot generation or time-based allocation logic
- Booking creation, amendments, or cancellations
- Payments, invoicing, or notifications
- User authentication or identity management

## Design Philosophy

- Separation of concerns: services = what is offered; providers = who delivers it; availability = when it can happen.
- Provider is not necessarily a user; a provider may or may not map to an authenticated account.
- Supports both human providers (e.g., tutors) and physical resources (e.g., rooms or equipment).
- Multi-tenant friendly: optional `PROVIDERS_TENANT_MODEL` adds required tenant FKs without forcing a specific tenancy package.
- Integrates cleanly into larger systems without forcing a specific architecture; it stays narrow and composable.

## Current Status

- Early development; public API may change.
- Focus is correctness, clarity, and extensibility over breadth.
- Breaking changes are expected before v1.0.

## Installation

Tested with Python 3.10+ and Django 4.2+.

```bash
pip install mroudai-django-providers
```

Add to `INSTALLED_APPS` and run migrations:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "providers",
    "services",  # your services app
]

# Optional settings
PROVIDERS_TENANT_MODEL = None  # e.g. "tenants.Tenant"
PROVIDERS_ALLOW_RESOURCE_PROVIDERS = True
```

```bash
python manage.py migrate
```

If `PROVIDERS_TENANT_MODEL` is set, provider-scoped models include a required `tenant` FK and uniqueness is enforced per tenant.

## Basic Usage Example

```python
from providers.models import Provider, ProviderService
from services.models import Service

# Create a human provider (global mode)
tutor = Provider.objects.create(
    name="Alex Tutor",
    provider_type=Provider.ProviderType.PERSON,
)

# Link a service to the provider's capability
maths = Service.objects.create(name="Maths 101", slug="maths-101")
ProviderService.objects.create(provider=tutor, service=maths)
```

In tenant mode, include `tenant=` on provider, service, and provider-service relations; the app enforces tenant consistency.

## Intended Use Cases

- Tutors and educators
- Salons and barbers
- Clinics and consultants
- Gyms and fitness instructors
- Resource-based bookings (rooms, courts, equipment)

## Relationship to Other Apps

`django-providers` is designed to sit alongside:
- services: defines what is offered.
- availability: defines when providers are available.
- slots / bookings (future): turns availability into bookable slots and handles reservations.

The providers app remains focused on "who" to keep integration points clear.

## Testing

- Tests use Django's `TestCase`.
- Coverage emphasises provider–service relationships, validation, tenancy enforcement, and model invariants.
- Run tests with the built-in runner: `python test providers` (executes both non-tenant and tenant configurations; `python test` also works).
- Contributions should include tests that exercise new behaviour or edge cases.

## Contributing

- Contributions are welcome; small, focused pull requests are preferred.
- Please discuss architectural changes and boundaries before large refactors.
- Respect the early-stage nature of the project and the likelihood of API changes.

## Licence

MIT Licence.
