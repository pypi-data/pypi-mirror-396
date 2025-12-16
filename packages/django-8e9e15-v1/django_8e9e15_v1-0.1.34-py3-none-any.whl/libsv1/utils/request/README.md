# Bear Django Request Utils

This is a core utility library for Django, designed to clean and normalize incoming request data (GET, POST, JSON, etc.) before it reaches your business logic. It solves the common problem of client applications (frontend, mobile apps) sending data in a non-unified format.

This package provides the base logic and is intended to be used within your own components, such as middleware.

---

## Key Features

- **None Normalization:** Converts strings like `"null"`, empty strings `""`, and the integer `0` for `id` or `_id` fields into a `None` value.
- **Boolean Normalization:** Converts string values like `"true"` and `"false"` (case-insensitive) into `True` and `False`.
- **String Cleaning:** Automatically trims leading/trailing whitespace and decodes URL-encoded characters (like `%20`).
- **Special Email Handling:** Removes spaces and lowercases email fields.
- **Universal:** Works with `GET` parameters, `application/json`, `multipart/form-data`, and `application/x-www-form-urlencoded`.
- **Configurable:** Allows you to specify which URL prefixes (e.g., `/api/`) the normalization should apply to.

---


---

## Concept and Usage

This package provides a `RequestUtils` class with a set of static methods. The main method is `normalize_request_params(request)`, which accepts a Django request object and modifies it in-place.

The best way to use this is by calling the method from within your own custom middleware.

---

### Example of creating middleware that uses this package

**your_project/middleware.py**

```python
from bear_request_utils import RequestUtils

class RequestNormalizerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Call the core logic from the package
        RequestUtils.normalize_request_params(request)
        return self.get_response(request)
```

**Add your middleware to settings.py:**

```python
MIDDLEWARE = [
    # ...
    'your_project.middleware.RequestNormalizerMiddleware',
    # ...
]
```

---

## Configuration

To enable normalization, you must specify a list of URL prefixes for which it will be applied. This is done in your `settings.py`.

```python
# settings.py

# A list of URL prefixes for which normalization will be active.
API_PREFIXES = ['/api/v1/', '/api/v2/']
```

---

## Normalization Rules

| Input Value         | Key          | Output Value      | Explanation |
|----------------------|---------------|-------------------|--------------|
| `"null"`             | any           | `None`            | The string "null" becomes None |
| `"true"`             | any           | `True`            | The string "true" becomes True |
| `"false"`            | any           | `False`           | The string "false" becomes False |
| `0` (integer)        | `user_id`     | `None`            | 0 for _id or id fields becomes None |
| `"0"` (string)       | `id`          | `None`            | The string "0" for _id or id fields becomes None |
| `""` (empty string)  | `category_id` | `None`            | An empty string for _id or id fields becomes None |
| `" test%20string "`  | `name`        | `"test string"`   | Whitespace is trimmed and characters are decoded |
| `" User@Example.com "` | `email`     | `"user@example.com"` | Whitespace is removed and the string is lowercased |

---

## License

This project is licensed under the MIT License.
