"""NetBox SCION API package.

Import serializers on package import so NetBox's serializer registry
is populated early and SerializerNotFound is avoided during form render.
"""

# Import for side effects (register serializers)
try:  # pragma: no cover
    from . import serializers as _serializers  # noqa: F401
except Exception:
	# If serializers fail to import, API may be partially unavailable
	# but avoid crashing plugin load.
	pass

