import django_tables2 as tables
from django.utils.html import format_html
from netbox.tables import NetBoxTable
from .models import Organization, ISDAS, SCIONLink


class OrganizationTable(NetBoxTable):
    short_name = tables.Column(
        linkify=True
    )
    full_name = tables.Column()
    isd_ases_count = tables.Column(
        verbose_name='ISD-ASes',
        orderable=False,
        empty_values=()
    )

    class Meta(NetBoxTable.Meta):
        model = Organization
        fields = ('pk', 'id', 'short_name', 'full_name', 'description', 'isd_ases_count')
        default_columns = ('short_name', 'full_name', 'description', 'isd_ases_count')

    def render_isd_ases_count(self, record):
        return record.isd_ases.count()


class ISDATable(NetBoxTable):
    isd_as = tables.Column(
        linkify=True
    )
    organization = tables.Column(
        linkify=True,
        empty_values=()
    )
    appliances = tables.Column(
        verbose_name='Appliances',
        orderable=False,
        empty_values=()
    )
    links_count = tables.Column(
        verbose_name='Links',
        orderable=False,
        empty_values=()
    )

    class Meta(NetBoxTable.Meta):
        model = ISDAS
        fields = ('pk', 'id', 'isd_as', 'organization', 'description', 'appliances', 'links_count')
        default_columns = ('isd_as', 'organization', 'description', 'appliances', 'links_count')

    def render_appliances(self, record):
        return len(record.appliances) if record.appliances else 0

    def render_organization(self, value, record):
        """Render organization with proper null handling"""
        if value and value.pk:
            return format_html('<a href="{}">{}</a>', value.get_absolute_url(), value.short_name)
        return '—'

    def render_links_count(self, record):
        return record.links.count()


class SCIONLinkTable(NetBoxTable):
    isd_as = tables.Column(
        linkify=True
    )
    core = tables.Column(
        verbose_name='Appliance'
    )
    interface_id = tables.Column(
        verbose_name='Interface ID',
        linkify=True
    )
    relationship = tables.Column(
        verbose_name='Relationship'
    )
    status = tables.Column(
        verbose_name='Status'
    )
    peer_name = tables.Column()
    peer = tables.Column()
    ticket = tables.Column(
        verbose_name='Ticket'
    )
    local_underlay = tables.Column(
        verbose_name='Local Underlay'
    )
    peer_underlay = tables.Column(
        verbose_name='Peer Underlay'
    )

    class Meta(NetBoxTable.Meta):
        model = SCIONLink
        fields = ('pk', 'id', 'isd_as', 'core', 'interface_id', 'relationship', 'status', 'peer_name', 'peer', 'local_underlay', 'peer_underlay', 'ticket')
        default_columns = ('isd_as', 'core', 'interface_id', 'relationship', 'status', 'peer_name', 'peer', 'local_underlay', 'peer_underlay', 'ticket')

    def render_ticket(self, value, record):
        if not value:
            return ''
        url = record.get_ticket_url()
        if url:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>', url, value)
        return value

    STATUS_COLORS = {
        'ACTIVE': ('#28a745', '#fff'),
        'RESERVED': ('#ffc107', '#000'),
        'PLANNED': ('#6c757d', '#fff'),
    }
    REL_COLORS = {
        'CORE': ('#4f46e5', '#fff'),
        'CHILD': ('#14b8a6', '#fff'),
        'PARENT': ('#3b82f6', '#fff'),
    }

    def _badge(self, text, bg, fg):
        return format_html('<span class="badge" style="background-color:{};color:{};font-weight:500;">{}</span>', bg, fg, text)

    def render_status(self, value):
        if not value:
            return ''
        # Normalize to uppercase for consistent color lookup even if DB holds mixed-case values
        key = value.upper()
        bg, fg = self.STATUS_COLORS.get(key, ('#6c757d', '#fff'))
        label = key.title()
        return self._badge(label, bg, fg)

    def render_relationship(self, value):
        if not value:
            return ''
        bg, fg = self.REL_COLORS.get(value, ('#6c757d', '#fff'))
        # value already uppercase; display as given
        return self._badge(value.title() if value.isupper() else value, bg, fg)
