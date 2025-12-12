# Django Activity Tracking

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Django 4.0+](https://img.shields.io/badge/django-4.0%2B-darkgreen)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A plug-and-play Django app for comprehensive user activity tracking including create, update, delete, view, login, and logout actions.

## Features

- 🔄 **Automatic Tracking**: Tracks CREATE, UPDATE, DELETE operations via Django signals
- 👁️ **Manual Tracking**: API endpoint and helpers for VIEW actions
- 🔐 **Authentication Tracking**: Login and logout tracking
- 🎯 **Flexible Configuration**: Register models via settings or programmatically
- 🔒 **Sensitive Data Protection**: Exclude sensitive fields from tracking
- 📊 **REST API**: Built-in DRF endpoints with Swagger documentation
- 🎨 **Multiple Integration Patterns**: Helpers, decorators, and mixins
- 📝 **Change Tracking**: Detailed before/after values for updates
- 🌐 **IP & User Agent**: Captures request metadata

## Installation

```bash
pip install django-activity-tracking
```

## Quick Setup

### 1. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    'activity_tracking',
]
```

### 2. Add Middleware

```python
MIDDLEWARE = [
    ...
    'activity_tracking.middleware.ActivityTrackingMiddleware',
]
```

### 3. Configure Settings

```python
ACTIVITY_TRACKING_SENSITIVE_FIELDS = ['password', 'otp', 'token']
ACTIVITY_TRACKING_AUTO_REGISTER_MODELS = [
    'auth.User',
    'myapp.MyModel',
]
```

### 4. Add URLs

```python
urlpatterns = [
    ...
    path('api/activity/', include('activity_tracking.urls')),
]
```

### 5. Run Migrations

```bash
python manage.py migrate activity_tracking
```

## Usage

### Auto-Register Models

```python
ACTIVITY_TRACKING_AUTO_REGISTER_MODELS = [
    'auth.User',
    'myapp.MyModel',
]
```

### Manual Registration

```python
from activity_tracking.registry import registry
from myapp.models import MyModel

registry.register(MyModel)
```

### Track Login/Logout

```python
from activity_tracking.helpers import log_login, log_logout

# In login view
log_login(user, request)

# In logout view
log_logout(user, request)
```

### Using Decorator

```python
from activity_tracking.decorators import track_view

@track_view('myapp.mymodel', lambda r, pk: pk, lambda r, pk: f'Object {pk}')
def detail_view(request, pk):
    obj = MyModel.objects.get(pk=pk)
    return render(request, 'detail.html', {'object': obj})
```

### Using Mixin

```python
from activity_tracking.mixins import ActivityTrackingMixin
from activity_tracking.models import UserActivity

class MyDetailView(ActivityTrackingMixin, DetailView):
    model = MyModel
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.log_activity(UserActivity.ActionChoices.VIEW, self.object)
        return response
```

## API Endpoints

- `GET /api/activity/my-activities/` - Get logged-in user's activities
- `GET /api/activity/all-activities/` - Get all activities (Admin only)
- `POST /api/activity/log-view/` - Manually log view action

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ACTIVITY_TRACKING_SENSITIVE_FIELDS` | `['password', 'otp', 'last_login', 'token', 'secret']` | Fields to exclude from tracking |
| `ACTIVITY_TRACKING_AUTO_REGISTER_MODELS` | `[]` | Models to auto-register |
| `ACTIVITY_TRACKING_TRACK_LOGIN` | `True` | Enable login tracking |
| `ACTIVITY_TRACKING_TRACK_LOGOUT` | `True` | Enable logout tracking |
| `ACTIVITY_TRACKING_TRACK_IP` | `True` | Track IP addresses |
| `ACTIVITY_TRACKING_TRACK_USER_AGENT` | `True` | Track user agents |

## Requirements

- Python >= 3.8
- Django >= 4.0
- djangorestframework >= 3.14
- drf-spectacular >= 0.26.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
