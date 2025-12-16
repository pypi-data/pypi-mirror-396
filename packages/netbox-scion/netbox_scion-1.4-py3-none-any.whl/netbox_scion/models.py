from django.db import models
from django.core.exceptions import ValidationError
import ipaddress
from django.urls import reverse
from django.core.validators import RegexValidator
from netbox.models import NetBoxModel

try:
    from django.contrib.postgres.fields import ArrayField
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class Organization(NetBoxModel):
    """
    An organization that operates ISD-ASes.
    """
    short_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Short name for the organization (unique globally)"
    )
    full_name = models.CharField(
        max_length=200,
        help_text="Full name of the organization"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description"
    )
    comments = models.TextField(
        blank=True,
        help_text="Free-form comments (internal notes)"
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ['short_name']

    def __str__(self):
        return self.short_name

    @property
    def display(self):
        return self.short_name

    def get_absolute_url(self):
        return reverse('plugins:netbox_scion:organization', args=[self.pk])


class ISDAS(NetBoxModel):
    """
    An ISD-AS (Isolation Domain - Autonomous System) in the SCION network.
    """
    # Updated regex to support both formats: 1-ff00:0:110 and 1-1
    ISD_AS_REGEX = r'^\d+-([0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+|\d+)$'
    
    isd_as = models.CharField(
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                regex=ISD_AS_REGEX,
                message="ISD-AS must be in format '{isd}-{as}' (e.g., '1-ff00:0:110' or '1-1')",
                code='invalid_isd_as'
            )
        ],
        help_text="ISD-AS identifier in format '{isd}-{as}' (e.g., '1-ff00:0:110' or '1-1')"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description"
    )
    comments = models.TextField(
        blank=True,
        help_text="Free-form comments (internal notes)"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,  # Changed from PROTECT to CASCADE for auto-delete
        related_name='isd_ases',
        help_text="Organization that operates this ISD-AS"
    )
    
    # Use JSONField for consistency with NetBox
    appliances = models.JSONField(
        default=list,
        blank=True,
        help_text="List of appliances for this ISD-AS"
    )

    class Meta:
        verbose_name = "ISD-AS"
        verbose_name_plural = "ISD-ASes"
        ordering = ['isd_as']

    def __str__(self):
        return self.isd_as

    @property
    def display(self):
        return self.isd_as

    def get_absolute_url(self):
        return reverse('plugins:netbox_scion:isdas', args=[self.pk])

    @property
    def appliances_display(self):
        """Return appliances as a comma-separated string for display"""
        if isinstance(self.appliances, list):
            return ', '.join(self.appliances)
        return str(self.appliances)


class SCIONLink(NetBoxModel):
    """
    SCION link interface configuration.
    """
    
    # Relationship choices
    RELATIONSHIP_PARENT = 'PARENT'
    RELATIONSHIP_CHILD = 'CHILD'
    RELATIONSHIP_CORE = 'CORE'
    
    RELATIONSHIP_CHOICES = [
        (RELATIONSHIP_PARENT, 'PARENT'),
        (RELATIONSHIP_CHILD, 'CHILD'),
        (RELATIONSHIP_CORE, 'CORE'),
    ]

    # Status choices
    STATUS_RESERVED = 'RESERVED'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_PLANNED = 'PLANNED'

    STATUS_CHOICES = [
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PLANNED, 'Planned'),
    ]
    
    isd_as = models.ForeignKey(
        ISDAS,
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name="ISD-AS",
        help_text="ISD-AS that owns this interface"
    )
    core = models.CharField(
        max_length=255,
        verbose_name="Appliance",
        help_text="Appliance for this link"
    )
    interface_id = models.PositiveIntegerField(
        verbose_name="Interface ID",
        help_text="Interface ID (unique per ISD-AS)"
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name="Relationship",
        help_text="Relationship type of this SCION link"
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        help_text="Operational status of this link"
    )
    peer_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Peer name (optional)"
    )
    peer = models.CharField(
        max_length=255,
        blank=True,
        null=True,  # Allow NULL values
        help_text="Peer identifier (optional) in format '{isd}-{as}#{interface_number}' when provided"
    )
    local_underlay = models.CharField(
        max_length=300,
        blank=True,
        help_text="Local underlay endpoint in format ip:port (IPv4 or IPv6; bracketed IPv6 supported)"
    )
    peer_underlay = models.CharField(
        max_length=300,
        blank=True,
        help_text="Peer underlay endpoint in format ip:port (IPv4 or IPv6; bracketed IPv6 supported)"
    )
    # Store arbitrary user input meant to represent a URL. We intentionally do NOT validate
    # or constrain format so that any external system reference can be pasted (full URL,
    # partial path, ID, etc.). For display purposes we'll attempt to coerce it into a URL
    # when rendering (prefixing with https:// if it looks like a hostname or path).
    ticket = models.CharField(
        max_length=512,
        blank=True,
        help_text="External reference (treated as URL if possible; no validation enforced)"
    )
    comments = models.TextField(
        blank=True,
        help_text="Free-form comments (internal notes)"
    )

    class Meta:
        verbose_name = "SCION Link"
        verbose_name_plural = "SCION Links"
        ordering = ['isd_as', 'interface_id']
        constraints = [
            models.UniqueConstraint(
                fields=['isd_as', 'interface_id'],
                name='unique_interface_per_isdas'
            ),
            models.UniqueConstraint(
                fields=['isd_as', 'peer'],
                name='unique_peer_per_isdas',
                condition=models.Q(peer__isnull=False) & ~models.Q(peer='')
            )
        ]

    def __str__(self):
        return f"{self.isd_as} - Interface {self.interface_id}"

    @property
    def display(self):
        return f"{self.isd_as} - Interface {self.interface_id}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_scion:scionlink', args=[self.pk])

    def get_ticket_url(self):
        """Best-effort URL normalization of the stored ticket value.

        Rules (lightweight on purpose):
        - Empty/blank -> None
        - Already starts with a scheme (http:// or https:// or other) -> return as-is
        - Starts with '//' (protocol-relative) -> prefix with 'https:'
        - Looks like a domain (contains a dot, no spaces) -> prefix with 'https://'
        - Looks like a single path fragment or ID -> return None (caller can still show raw)
        """
        value = (self.ticket or '').strip()
        if not value:
            return None
        lower = value.lower()
        if lower.startswith('http://') or lower.startswith('https://') or '://' in value:
            return value
        if value.startswith('//'):
            return f"https:{value}"
        # Heuristic: treat as domain if it has at least one dot and no spaces
        if ' ' not in value and '.' in value:
            return f"https://{value}"
        return None

    def clean(self):
        super().clean()
        
        # Convert empty peer to NULL for proper unique constraint handling
        if hasattr(self, 'peer') and self.peer == '':
            self.peer = None
        
        # Validate underlay fields if provided
        for field_name in ('local_underlay', 'peer_underlay'):
            value = getattr(self, field_name, '') or ''
            if value:
                try:
                    ip_part, port_part = value.rsplit(':', 1)
                except ValueError:
                    raise ValidationError({field_name: 'Must be in format ip:port'})
                # Validate port
                if not port_part.isdigit() or int(port_part) <= 0:
                    raise ValidationError({field_name: 'Port must be a positive integer'})
                # Validate IP (IPv4 or IPv6)
                try:
                    # Strip brackets for IPv6 like [2001:db8::1]
                    if ip_part.startswith('[') and ip_part.endswith(']'):
                        candidate_ip = ip_part[1:-1]
                    else:
                        candidate_ip = ip_part
                    ipaddress.ip_address(candidate_ip)
                except ValueError:
                    raise ValidationError({field_name: 'Invalid IP address'})
