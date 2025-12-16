# Initial migration for netbox_scion plugin

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # Create Organization table
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('short_name', models.CharField(
                    max_length=100,
                    unique=True,
                    help_text="Short name for the organization (unique globally)"
                )),
                ('full_name', models.CharField(
                    max_length=200,
                    help_text="Full name of the organization"
                )),
                ('description', models.TextField(
                    blank=True,
                    help_text="Optional description"
                )),
                ('comments', models.TextField(
                    blank=True,
                    help_text="Free-form comments (internal notes)"
                )),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
                'ordering': ['short_name'],
            },
        ),
        
        # Create ISDAS table
        migrations.CreateModel(
            name='ISDAS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('isd_as', models.CharField(
                    max_length=32,
                    unique=True,
                    validators=[
                        django.core.validators.RegexValidator(
                            regex=r'^\d+-([0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+|\d+)$',
                            message="ISD-AS must be in format '{isd}-{as}' (e.g., '1-ff00:0:110' or '1-1')",
                            code='invalid_isd_as'
                        )
                    ],
                    help_text="ISD-AS identifier in format '{isd}-{as}' (e.g., '1-ff00:0:110' or '1-1')"
                )),
                ('description', models.TextField(
                    blank=True,
                    help_text="Optional description"
                )),
                ('comments', models.TextField(
                    blank=True,
                    help_text="Free-form comments (internal notes)"
                )),
                ('appliances', models.JSONField(
                    default=list,
                    blank=True,
                    help_text="List of appliances for this ISD-AS"
                )),
                ('organization', models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='isd_ases',
                    to='netbox_scion.organization',
                    help_text="Organization that operates this ISD-AS"
                )),
            ],
            options={
                'verbose_name': 'ISD-AS',
                'verbose_name_plural': 'ISD-ASes',
                'ordering': ['isd_as'],
            },
        ),
        
        # Create SCIONLink table
        migrations.CreateModel(
            name='SCIONLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('interface_id', models.PositiveIntegerField(
                    verbose_name="Interface ID",
                    help_text="Interface ID (unique per ISD-AS)"
                )),
                ('core', models.CharField(
                    max_length=255,
                    verbose_name="Appliance",
                    help_text="Appliance for this link"
                )),
                ('relationship', models.CharField(
                    max_length=20,
                    choices=[
                        ('PARENT', 'PARENT'),
                        ('CHILD', 'CHILD'),
                        ('CORE', 'CORE')
                    ],
                    verbose_name="Relationship",
                    help_text="Relationship type of this SCION link"
                )),
                ('status', models.CharField(
                    max_length=16,
                    choices=[
                        ('RESERVED', 'Reserved'),
                        ('ACTIVE', 'Active'),
                        ('PLANNED', 'Planned')
                    ],
                    default='ACTIVE',
                    help_text="Operational status of this link"
                )),
                ('peer_name', models.CharField(
                    max_length=100,
                    blank=True,
                    help_text="Peer name (optional)"
                )),
                ('peer', models.CharField(
                    max_length=255,
                    blank=True,
                    null=True,
                    help_text="Peer identifier (optional) in format '{isd}-{as}#{interface_number}' when provided"
                )),
                ('local_underlay', models.CharField(
                    max_length=300,
                    blank=True,
                    help_text="Local underlay endpoint in format ip:port (IPv4 or IPv6; bracketed IPv6 supported)"
                )),
                ('peer_underlay', models.CharField(
                    max_length=300,
                    blank=True,
                    help_text="Peer underlay endpoint in format ip:port (IPv4 or IPv6; bracketed IPv6 supported)"
                )),
                ('ticket', models.CharField(
                    max_length=512,
                    blank=True,
                    help_text="External reference (treated as URL if possible; no validation enforced)"
                )),
                ('comments', models.TextField(
                    blank=True,
                    help_text="Free-form comments (internal notes)"
                )),
                ('isd_as', models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='links',
                    to='netbox_scion.isdas',
                    verbose_name="ISD-AS",
                    help_text="ISD-AS that owns this interface"
                )),
            ],
            options={
                'verbose_name': 'SCION Link',
                'verbose_name_plural': 'SCION Links',
                'ordering': ['isd_as', 'interface_id'],
            },
        ),
        
        # Add unique constraint for interface_id per ISD-AS
        migrations.AddConstraint(
            model_name='scionlink',
            constraint=models.UniqueConstraint(
                fields=['isd_as', 'interface_id'],
                name='unique_interface_per_isdas'
            ),
        ),
        
        # Add conditional unique constraint for peer per ISD-AS
        # Only enforces uniqueness when peer is not NULL and not empty string
        migrations.AddConstraint(
            model_name='scionlink',
            constraint=models.UniqueConstraint(
                fields=['isd_as', 'peer'],
                name='unique_peer_per_isdas',
                condition=models.Q(peer__isnull=False) & ~models.Q(peer='')
            ),
        ),
    ]
