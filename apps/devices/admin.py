from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.db.models import Count
from django.utils.html import format_html
from .models import (
    Device, SolarPanel, Generator, Battery,
    ElectricVehicle, AirConditioner, Heater
)


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with enhanced dashboard."""

    def index(self, request, extra_context=None):
        """Custom index view with statistics."""
        extra_context = extra_context or {}

        # Calculate statistics
        extra_context['production_count'] = SolarPanel.objects.count() + Generator.objects.count()
        extra_context['storage_count'] = Battery.objects.count() + ElectricVehicle.objects.count()
        extra_context['consumption_count'] = AirConditioner.objects.count() + Heater.objects.count()
        extra_context['user_count'] = User.objects.count()

        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')
admin_site.site_header = "⚡ Daylight Energy Administration"
admin_site.site_title = "Daylight Energy Admin"
admin_site.index_title = "Smart Home Energy Management"


class DeviceAdmin(admin.ModelAdmin):
    """Base admin for Device model."""
    list_display = ['device_icon', 'name', 'user', 'status_badge', 'get_device_type', 'created_at']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_device_type']
    ordering = ['-created_at']
    list_per_page = 20

    def device_icon(self, obj):
        """Display device icon."""
        icons = {
            'solar_panel': '☀️',
            'generator': '⚙️',
            'battery': '🔋',
            'electric_vehicle': '🚗',
            'air_conditioner': '❄️',
            'heater': '🔥'
        }
        icon = icons.get(obj.get_device_type(), '⚡')
        return format_html('<span style="font-size: 24px;">{}</span>', icon)
    device_icon.short_description = ''

    def status_badge(self, obj):
        """Display status with badge."""
        if obj.status == 'online':
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(0, 255, 136, 0.15); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 12px; color: #00ff88; font-weight: 600; font-size: 12px;">'
                '<span style="width: 8px; height: 8px; background: #00ff88; border-radius: 50%; animation: pulse 2s infinite;"></span>ONLINE</span>'
            )
        else:
            return format_html(
                '<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(148, 163, 184, 0.15); border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 12px; color: #94a3b8; font-weight: 600; font-size: 12px;">'
                '<span style="width: 8px; height: 8px; background: #64748b; border-radius: 50%;"></span>OFFLINE</span>'
            )
    status_badge.short_description = 'Status'

    def get_device_type(self, obj):
        return obj.get_device_type().replace('_', ' ').title()
    get_device_type.short_description = 'Device Type'

    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }


class SolarPanelAdmin(DeviceAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'status'),
            'description': '☀️ Solar panel energy production device'
        }),
        ('Solar Panel Specifications', {
            'fields': ('panel_area_m2', 'efficiency', 'max_capacity_w', 'latitude', 'longitude'),
            'description': 'Configure panel size, efficiency, and location for accurate solar calculations'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class GeneratorAdmin(DeviceAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'status'),
            'description': '⚙️ Backup generator device'
        }),
        ('Generator Specifications', {
            'fields': ('rated_output_w',),
            'description': 'Configure rated power output'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class BatteryAdmin(DeviceAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'status'),
            'description': '🔋 Battery storage device configuration'
        }),
        ('Battery Specifications', {
            'fields': ('capacity_kwh', 'current_charge_kwh', 'max_charge_rate_kw', 'max_discharge_rate_kw'),
            'description': 'Configure battery capacity and charge/discharge rates'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_display = DeviceAdmin.list_display + ['charge_bar']

    def charge_bar(self, obj):
        """Display charge percentage with visual bar."""
        percentage = obj.charge_percentage
        color = '#00d4ff' if percentage > 20 else '#ff8c42'
        percentage_str = f'{percentage:.1f}'
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px; min-width: 200px;">'
            '<div style="flex: 1; height: 12px; background: rgba(255,255,255,0.05); border-radius: 6px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; border-radius: 6px; transition: width 0.3s;"></div>'
            '</div>'
            '<span style="font-family: monospace; font-weight: 600; color: {};">{}%</span>'
            '</div>',
            percentage, color, color, percentage_str
        )
    charge_bar.short_description = 'Charge Level'


class ElectricVehicleAdmin(DeviceAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'status'),
            'description': '🚗 Electric vehicle configuration'
        }),
        ('EV Specifications', {
            'fields': ('capacity_kwh', 'current_charge_kwh', 'max_charge_rate_kw', 'max_discharge_rate_kw'),
            'description': 'Configure battery capacity and charge/discharge rates'
        }),
        ('EV State & Schedule', {
            'fields': ('mode', 'last_seen_at', 'driving_efficiency_kwh_per_hour'),
            'description': 'Vehicle mode and driving efficiency settings'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_display = DeviceAdmin.list_display + ['mode_badge', 'charge_bar']
    list_filter = DeviceAdmin.list_filter + ['mode']

    def mode_badge(self, obj):
        """Display mode with badge."""
        colors = {
            'charging': ('#00d4ff', 'rgba(0, 212, 255, 0.15)', 'rgba(0, 212, 255, 0.3)'),
            'discharging': ('#ff8c42', 'rgba(255, 140, 66, 0.15)', 'rgba(255, 140, 66, 0.3)'),
            'offline': ('#64748b', 'rgba(148, 163, 184, 0.15)', 'rgba(148, 163, 184, 0.3)')
        }
        color, bg, border = colors.get(obj.mode, colors['offline'])
        return format_html(
            '<span style="display: inline-flex; align-items: center; padding: 4px 12px; background: {}; border: 1px solid {}; border-radius: 12px; color: {}; font-weight: 600; font-size: 12px; text-transform: uppercase;">{}</span>',
            bg, border, color, obj.mode
        )
    mode_badge.short_description = 'Mode'

    def charge_bar(self, obj):
        """Display charge percentage with visual bar."""
        percentage = obj.charge_percentage
        color = '#00d4ff' if percentage > 20 else '#ff8c42'
        percentage_str = f'{percentage:.1f}'
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px; min-width: 200px;">'
            '<div style="flex: 1; height: 12px; background: rgba(255,255,255,0.05); border-radius: 6px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; border-radius: 6px; transition: width 0.3s;"></div>'
            '</div>'
            '<span style="font-family: monospace; font-weight: 600; color: {};">{}%</span>'
            '</div>',
            percentage, color, color, percentage_str
        )
    charge_bar.short_description = 'Charge Level'


class AirConditionerAdmin(DeviceAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'status'),
            'description': '❄️ Air conditioning consumption device'
        }),
        ('AC Specifications', {
            'fields': ('rated_power_w', 'min_power_w', 'max_power_w'),
            'description': 'Configure power consumption range (rated, minimum, and maximum)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class HeaterAdmin(DeviceAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'status'),
            'description': '🔥 Electric heater consumption device'
        }),
        ('Heater Specifications', {
            'fields': ('rated_power_w', 'min_power_w', 'max_power_w'),
            'description': 'Configure power consumption range (rated, minimum, and maximum)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(UserAdmin):
    """Custom User admin with simplified action dropdown for debugging."""
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist to customize action dropdown."""
        extra_context = extra_context or {}
        extra_context['default_action'] = 'delete_selected'
        return super().changelist_view(request, extra_context)
    
    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }
        js = ('js/admin-actions.js',)


# Register all models to the custom admin site
admin_site.register(SolarPanel, SolarPanelAdmin)
admin_site.register(Generator, GeneratorAdmin)
admin_site.register(Battery, BatteryAdmin)
admin_site.register(ElectricVehicle, ElectricVehicleAdmin)
admin_site.register(AirConditioner, AirConditionerAdmin)
admin_site.register(Heater, HeaterAdmin)
admin_site.register(Device, DeviceAdmin)

# Register Django built-in models with custom admins
admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, GroupAdmin)
