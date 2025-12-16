# streamlit-html-components

**Use traditional HTML/CSS/JS file structure with Streamlit** while keeping the benefits of free Streamlit deployment.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://pypi.org/project/streamlit-html-components/)

## ✨ What's New in v0.3.0

- 🔥 **Hot Reload** - Component files auto-reload during development
- 🔄 **State Management** - Real-time state sync with conflict resolution
- 📋 **Event Replay** - Record and replay component events
- ✅ **Props Validation** - JSON Schema validation for component props
- 📦 **Component Registry** - Early validation at startup

## Features

### Core Features
- 📁 **Organized File Structure** - Separate HTML/CSS/JS files (traditional web development workflow)
- 🔄 **Template Variables** - Jinja2-powered props and data binding
- 🎨 **Framework Integration** - Easy setup with Tailwind, Bootstrap, Bulma, and more
- ⚡ **Performance Caching** - Multi-level caching for fast rendering
- 🚀 **Streamlit Cloud Ready** - Works with free Streamlit deployment
- 🛡️ **Security Built-in** - XSS prevention and input validation

### Advanced Features (v0.3.0)
- 🔥 **Hot Reload** - Component files auto-reload during development (no restart needed!)
- 🔌 **Enhanced Bidirectional Communication** - State management, event replay, conflict resolution
- ✅ **Props Validation** - JSON Schema or manual validation rules
- 📦 **Component Registry** - Validate components at startup, not render time
- 🔍 **Fuzzy Matching** - Smart error messages with suggestions
- 📊 **State History** - Track and rollback state changes
- 🎯 **Event Recording** - Automatic event history with replay capability

## Installation

```bash
pip install streamlit-html-components
```

Or install from source:

```bash
git clone https://github.com/cjcarito/streamlit-html-components
cd streamlit-html-components
pip install -e .
```

## Quick Start

### 1. Create Your Component Files

```
my_app/
├── app.py
└── components/
    ├── templates/
    │   └── button.html
    ├── styles/
    │   └── button.css
    └── scripts/
        └── button.js
```

**templates/button.html:**
```html
<button class="custom-btn" id="myBtn">
    {{ text }}
</button>
```

**styles/button.css:**
```css
.custom-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 32px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
```

**scripts/button.js:**
```javascript
document.getElementById('myBtn').addEventListener('click', function() {
    alert('Button clicked!');
});
```

### 2. Use in Your Streamlit App

**app.py:**
```python
import streamlit as st
from streamlit_html_components import render_component, configure

# Configure component directories
configure(
    templates_dir='components/templates',
    styles_dir='components/styles',
    scripts_dir='components/scripts'
)

st.title("My Custom Button")

# Render your component
render_component(
    'button',  # Component name (matches template filename)
    props={'text': 'Click me!'},  # Variables passed to template
    height=100
)
```

### 3. Run Your App

```bash
streamlit run app.py
```

That's it! Your custom HTML/CSS/JS component is now running in Streamlit.

## Modern v2 API (Recommended)

The v2 API provides enhanced features with better validation, immutable configuration, and improved performance.

### Key Benefits

- ✅ **Component Registry** - Validate components at startup, not render time
- 🔒 **Immutable Configuration** - Pydantic-based type-safe configuration
- 🚀 **Better Caching** - Cache keys based on actual file content
- 📝 **Better Error Messages** - Detailed validation errors with suggestions
- 🔍 **Auto-discovery** - Automatically find and register components

### Quick Start with v2

```python
import streamlit as st
from streamlit_html_components import configure_v2, render_component_v2

# Configure with auto-discovery
configure_v2(
    templates_dir='components/templates',
    styles_dir='components/styles',
    scripts_dir='components/scripts',
    frameworks=['tailwind'],
    auto_discover=True  # Automatically register all components
)

st.title("My App with v2 API")

# Render component (validated at startup)
render_component_v2('button', props={'text': 'Click me!'})
```

### v2 API Reference

#### `configure_v2()`

Modern configuration with Pydantic validation:

```python
from streamlit_html_components import configure_v2

configure_v2(
    templates_dir='components/templates',
    styles_dir='components/styles',
    scripts_dir='components/scripts',
    frameworks=['tailwind', 'bootstrap'],

    # Cache settings
    enable_cache=True,
    cache_max_size_mb=100,
    cache_ttl_seconds=300,

    # Security settings
    enable_csp=True,
    allowed_origins=['*'],
    validate_paths=True,

    # Auto-discovery
    auto_discover=True  # Scan and register all components
)
```

#### `render_component_v2()`

Render components with registry validation:

```python
from streamlit_html_components import render_component_v2

render_component_v2(
    component_name='button',
    props={'text': 'Click me'},
    height=100,
    cache=True,
    on_event=callback_function
)
```

#### `register_component()`

Manually register components:

```python
from streamlit_html_components import register_component

register_component(
    name='custom_button',
    template='button.html',
    styles=['button.css', 'animations.css'],
    scripts=['button.js'],
    validate=True  # Validate files exist at registration time
)
```

#### `list_components()`

List all registered components:

```python
from streamlit_html_components import list_components

components = list_components()
print(components)  # ['button', 'card', 'hero', ...]
```

#### `get_component_info()`

Get component metadata:

```python
from streamlit_html_components import get_component_info

info = get_component_info('button')
print(info.template)  # 'button.html'
print(info.styles)    # ['button.css']
print(info.scripts)   # ['button.js']
```

### Migration from v1 to v2

The v2 API is backward compatible. You can use both APIs in the same app:

```python
from streamlit_html_components import (
    configure, render_component,      # v1 API
    configure_v2, render_component_v2  # v2 API
)

# Use v1 for backward compatibility
configure(templates_dir='old_components/templates')
render_component('legacy_button', props={'text': 'Old API'})

# Use v2 for new components
configure_v2(templates_dir='new_components/templates', auto_discover=True)
render_component_v2('modern_button', props={'text': 'New API'})
```

**Why migrate to v2?**

1. **Earlier error detection** - Components validated at startup
2. **Better caching** - Invalidates cache when files change
3. **Type safety** - Pydantic validates all configuration
4. **Immutability** - Configuration can't be accidentally modified
5. **Better DX** - Auto-discovery reduces boilerplate

## Core API (v1 - Legacy)

### `render_component()`

The main function to render components:

```python
render_component(
    component_name: str,              # Name of component (e.g., 'button')
    props: Dict[str, Any] = None,     # Variables for template

    # Directory overrides (optional)
    templates_dir: str = None,
    styles_dir: str = None,
    scripts_dir: str = None,

    # Asset control (optional)
    styles: List[str] = None,         # CSS files to load
    scripts: List[str] = None,        # JS files to load
    frameworks: List[str] = None,     # External frameworks

    # Display options
    height: int = None,               # Component height in pixels
    width: int = None,
    scrolling: bool = False,
    key: str = None,                  # Streamlit component key

    # Performance
    cache: bool = None,               # Enable caching
    cache_ttl: int = None,            # Cache time-to-live (seconds)

    # Interactivity
    on_event: Callable = None         # Callback for JS events
)
```

### `configure()`

Set global defaults for all components:

```python
from streamlit_html_components import configure

configure(
    templates_dir='components/templates',
    styles_dir='components/styles',
    scripts_dir='components/scripts',
    default_cache=True,
    external_frameworks=['tailwind']
)
```

### `add_framework()`

Add custom CSS/JS frameworks:

```python
from streamlit_html_components import add_framework

add_framework(
    'my_framework',
    css_urls=['https://cdn.example.com/framework.css'],
    js_urls=['https://cdn.example.com/framework.js']
)
```

## Template Features (Jinja2)

### Variable Interpolation

```html
<h1>{{ title }}</h1>
<p>{{ description }}</p>
```

### Conditionals

```html
{% if user_logged_in %}
    <button>Logout</button>
{% else %}
    <button>Login</button>
{% endif %}
```

### Loops

```html
<ul>
{% for item in items %}
    <li>{{ item.name }}: {{ item.price | currency }}</li>
{% endfor %}
</ul>
```

### Custom Filters

Built-in filters:
- `{{ price | currency }}` → "$1,234.56"
- `{{ date | date("%B %d, %Y") }}` → "December 10, 2025"
- `{{ 0.156 | percentage }}` → "15.6%"

### Template Inheritance

**base.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

**button.html:**
```html
{% extends "base.html" %}

{% block title %}My Button{% endblock %}

{% block content %}
    <button>{{ text }}</button>
{% endblock %}
```

## External Framework Integration

### Tailwind CSS

```python
configure(external_frameworks=['tailwind'])

render_component('card', props={
    'title': 'Product Card',
    'price': 99.99
})
```

**card.html:**
```html
<div class="max-w-sm rounded-lg shadow-lg bg-white p-6">
    <h2 class="text-2xl font-bold text-gray-800">{{ title }}</h2>
    <p class="text-3xl text-indigo-600">{{ price | currency }}</p>
</div>
```

### Bootstrap

```python
configure(external_frameworks=['bootstrap'])
```

### Bulma

```python
configure(external_frameworks=['bulma'])
```

### Custom Frameworks

```python
add_framework(
    'my_ui_kit',
    css_urls=['https://cdn.example.com/ui-kit.css'],
    js_urls=['https://cdn.example.com/ui-kit.js']
)

configure(external_frameworks=['my_ui_kit'])
```

## Caching for Performance

Components are cached by default for optimal performance:

```python
# Enable caching (default)
render_component('button', props={'text': 'Click'}, cache=True)

# Set cache expiration (30 seconds)
render_component('button', props={'text': 'Click'}, cache_ttl=30)

# Disable caching for dynamic content
render_component('live_data', props={'data': data}, cache=False)

# Clear cache manually
from streamlit_html_components import invalidate_cache

invalidate_cache('button')  # Clear specific component
invalidate_cache()          # Clear all cache
```

**Cache Statistics:**

```python
from streamlit_html_components import cache_stats

stats = cache_stats()
# {'total_entries': 5, 'total_size_kb': 45.2, ...}
```

## 🔥 Hot Reload (v0.3.0)

Enable instant component updates during development - no Streamlit restart needed!

```python
from streamlit_html_components import configure_v2, enable_hot_reload

# Configure your components
configure_v2(
    templates_dir='components/templates',
    styles_dir='components/styles',
    scripts_dir='components/scripts'
)

# Enable hot reload with one line!
enable_hot_reload(verbose=True)

# Now edit your component files and see changes instantly! 🔥
```

**What gets watched:**
- `templates/*.html` - Component templates
- `styles/*.css` - CSS stylesheets
- `scripts/*.js` - JavaScript files

**How it works:**
1. FileWatcher detects file changes (using watchdog or polling)
2. DevServer invalidates cache for affected components
3. Streamlit auto-reruns and shows updated component
4. Zero manual intervention required!

**Optional dependency:**
```bash
pip install watchdog  # For instant file detection (recommended)
# Without watchdog, falls back to polling mode (still works!)
```

## 🔄 Enhanced Bidirectional Communication (v0.3.0)

### Basic Communication

Send data from JavaScript to Python:

**button.js:**
```javascript
document.getElementById('myBtn').addEventListener('click', function() {
    // Send event to Python
    window.sendToStreamlit('click', {
        clicks: clickCount,
        timestamp: new Date().toISOString()
    });
});
```

**app.py:**
```python
def on_button_click(data):
    st.write(f"Received: {data}")
    st.session_state.clicks = data['clicks']

render_component(
    'button',
    props={'text': 'Click me'},
    on_event=on_button_click  # Python callback
)
```

### State Management (v0.3.0)

Real-time state synchronization with conflict resolution:

```python
from streamlit_html_components.bidirectional import StateManager, ConflictResolution

# Create state manager
state_manager = StateManager(
    conflict_resolution=ConflictResolution.MERGE,
    max_history=100
)

# Set initial state
state_manager.set_state('counter', {'count': 0, 'step': 1})

# Subscribe to state changes
def on_state_change(snapshot):
    st.write(f"State updated: {snapshot.state}")

state_manager.subscribe('counter', on_state_change)

# Sync from client (JavaScript)
success, conflicts = state_manager.sync_from_client(
    'counter',
    client_state={'count': 5},
    client_version=1
)
```

**Conflict Resolution Strategies:**
- `CLIENT_WINS` - Client updates always accepted
- `SERVER_WINS` - Server state maintained
- `LATEST_WINS` - Most recent update wins
- `MERGE` - Intelligent merging of changes
- `CUSTOM` - User-defined resolution function

**State Features:**
- Version tracking for every state change
- Complete state history with rollback
- State diffing (added/modified/removed)
- Export/import as JSON
- Real-time change notifications

### Event Replay (v0.3.0)

Record and replay component events for debugging and testing:

```python
from streamlit_html_components.bidirectional import get_bridge

bridge = get_bridge()

# Events are automatically recorded
bridge.handle_event('my_component', {
    'event': 'click',
    'data': {'button_id': 'submit'}
})

# Get event history
events = bridge.get_event_history('my_component')

# Replay all events
bridge.replay_events('my_component')

# Export events as JSON
json_data = bridge.export_events('my_component')
```

## ✅ Props Validation (v0.3.0)

Validate component props with JSON Schema or manual rules:

### JSON Schema Validation

```python
from streamlit_html_components import register_component, PropsSchema

# Define schema
schema = PropsSchema({
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
})

# Register component with validation
register_component(
    name='user_form',
    template='user_form.html',
    props_schema=schema
)

# Invalid props will raise InvalidPropsError
render_component_v2('user_form', props={
    'name': '',  # ❌ Fails: minLength validation
    'age': -5,   # ❌ Fails: minimum validation
})
```

### Manual Validation Rules

```python
from streamlit_html_components import PropsSchema, ValidationRule, ValidationType

schema = PropsSchema()

# Add validation rules
schema.add_rule(ValidationRule(
    prop_name='email',
    validation_type=ValidationType.PATTERN,
    rule=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    error_message='Must be a valid email'
))

schema.add_rule(ValidationRule(
    prop_name='age',
    validation_type=ValidationType.RANGE,
    rule={'min': 0, 'max': 120},
    error_message='Age must be between 0 and 120'
))

# Validate props
is_valid, errors = schema.validate({'email': 'test@example.com', 'age': 25})
```

**Validation Types:**
- `REQUIRED` - Field must be present
- `TYPE` - Value type checking (str, int, float, bool, list, dict)
- `PATTERN` - Regex pattern matching
- `RANGE` - Min/max value validation
- `ENUM` - Value must be in allowed list
- `CUSTOM` - Custom validation function

## Advanced Usage

### Multiple CSS/JS Files

```python
render_component(
    'complex_component',
    styles=['common', 'component', 'theme'],
    scripts=['utils', 'component', 'init']
)
```

### Conditional Asset Loading

```python
# Skip CSS loading
render_component('text_only', styles=[])

# Skip JS loading
render_component('static_card', scripts=[])
```

### Dynamic Props

```python
import streamlit as st

user_name = st.text_input("Your name")
user_email = st.text_input("Your email")

render_component('profile_card', props={
    'name': user_name,
    'email': user_email,
    'joined_date': datetime.now()
})
```

## Examples

The package includes complete working examples:

1. **Basic Button** (`examples/basic_button/`)
   - Simple component with HTML/CSS/JS
   - Click counting and callbacks
   - Component customization

2. **Tailwind Card** (`examples/tailwind_card/`)
   - External framework integration
   - Product card with pricing
   - Interactive builder

3. **Payslip Integration** (`examples/payslip_integration/`)
   - Real-world use case
   - Integration with existing Streamlit app

To run examples:

```bash
cd examples/basic_button
streamlit run app.py
```

## File Organization Conventions

### Auto-discovery

By default, `render_component('button')` automatically loads:
- `templates/button.html` (required)
- `styles/button.css` (optional)
- `scripts/button.js` (optional)

### Explicit Loading

```python
render_component(
    'button',
    styles=['button', 'animations'],  # Load multiple CSS files
    scripts=['button', 'utils']       # Load multiple JS files
)
```

### Custom Directories

```python
render_component(
    'button',
    templates_dir='custom/templates',
    styles_dir='custom/styles',
    scripts_dir='custom/scripts'
)
```

## Security

### XSS Prevention

- **Automatic HTML escaping** via Jinja2 auto-escaping
- **Props validation** and sanitization
- **Path traversal protection**

### Safe Template Variables

```html
<!-- Automatically escaped -->
<div>{{ user_input }}</div>

<!-- Explicit unsafe (use carefully) -->
<div>{{ trusted_html | safe }}</div>
```

## API Reference

### Core Functions (v2 - Recommended)

| Function | Description |
|----------|-------------|
| `configure_v2()` | Configure with Pydantic validation and auto-discovery |
| `render_component_v2()` | Render component with registry validation |
| `register_component()` | Manually register a component |
| `list_components()` | List all registered components |
| `get_component_info()` | Get component metadata |
| `get_config_v2()` | Get current v2 configuration |
| `get_registry()` | Get component registry instance |

### Core Functions (v1 - Legacy)

| Function | Description |
|----------|-------------|
| `render_component()` | Render an HTML component |
| `configure()` | Set global configuration |
| `add_framework()` | Add custom framework |

### Cache Management

| Function | Description |
|----------|-------------|
| `invalidate_cache()` | Clear component cache |
| `cache_stats()` | Get cache statistics |

### Configuration

| Function | Description |
|----------|-------------|
| `get_config()` | Get current configuration |
| `reset_config()` | Reset to defaults |

### Exceptions

| Exception | Raised When |
|-----------|-------------|
| `ComponentNotFoundError` | Template file not found |
| `AssetNotFoundError` | CSS/JS file not found |
| `TemplateSyntaxError` | Template syntax error |
| `InvalidPropsError` | Props validation fails |
| `ConfigurationError` | Invalid configuration |

## Troubleshooting

### Component not rendering

```python
# Check configuration
from streamlit_html_components import get_config
config = get_config()
print(config)

# Verify file paths
import os
print(os.listdir('templates'))
```

### CSS/JS not loading

```python
# Explicit file specification
render_component(
    'button',
    styles=['button'],  # Explicitly specify CSS file
    scripts=['button']  # Explicitly specify JS file
)
```

### Cache issues

```python
# Clear cache
from streamlit_html_components import invalidate_cache
invalidate_cache()

# Disable caching for debugging
render_component('button', cache=False)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Template engine powered by [Jinja2](https://jinja.palletsprojects.com/)
- Inspired by the need for traditional web development workflows in Streamlit

## Support

- **Documentation**: [GitHub Repository](https://github.com/cjcarito/streamlit-html-components)
- **Issues**: [GitHub Issues](https://github.com/cjcarito/streamlit-html-components/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cjcarito/streamlit-html-components/discussions)

---

**Made with ❤️ for the Streamlit community**
