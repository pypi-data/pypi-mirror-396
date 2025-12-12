# oarepo-glitchtip

Integration with glitchtip error monitoring service.

## Installation

1. Add oarepo-glitchtip to your dependencies in `pyproject.toml`:

```toml
[project]
name = "repo"
version = "1.0.0"
description = ""
packages = []
authors = []
dependencies = [
    "oarepo-glitchtip"
    # ...
]
# ...
```

2. At the top of your `invenio.cfg` file, add the following code:

```python
# glitchtip
from oarepo_glitchtip import initialize_glitchtip

initialize_glitchtip()
```

3. In the deployment, set the following environment variables:

```bash
export INVENIO_GLITCHTIP_DSN="<from your installed glitchtip server>"

# optionally
export DEPLOYMENT_VERSION="<version of the deployment>"
```

4. Run the repository as usual