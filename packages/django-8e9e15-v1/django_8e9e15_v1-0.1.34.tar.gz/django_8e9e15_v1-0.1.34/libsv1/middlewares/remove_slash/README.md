# Django Remove Trailing Slash

A simple Django middleware that enforces a "no trailing slash" policy by permanently redirecting (301) any URL ending in a slash to its non-slashed version.

This is useful for SEO purposes to prevent duplicate content indexing.

## Features

-   Performs a 301 Permanent Redirect.
-   Preserves query strings.
-   Ignores the root path (`/`).
-   Allows configurable exclusion of URL prefixes (e.g., `/admin/`, `/api/`).


## Usage

1.  Add the middleware to your `MIDDLEWARE` list in `settings.py`. It is recommended to place it before Django's `CommonMiddleware`.

```python
# settings.py
MIDDLEWARE = [
   'libsv1.middlewares.remove_slash.RemoveTrailingSlashMiddleware',
    # ... other middleware
]
```

2.  (Optional) By default, the middleware ignores URLs starting with `/admin/`. You can customize this by adding `REMOVE_SLASH_IGNORE_PREFIXES` to your `settings.py`.

```python
# settings.py
REMOVE_SLASH_IGNORE_PREFIXES = ['/admin/', '/api/v1/']
```

That's it! The middleware will now automatically handle redirects.