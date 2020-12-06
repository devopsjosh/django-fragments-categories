from django.contrib import admin
from fragment_categories.forms import CategoryAdminForm
from fragment_categories.models import Category, Hierarchy


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    search_fields = ['name', 'path']
    list_display = [
        '__str__', 'slug_path', 'name', 'path', 'featured'
    ]
    list_filter = ('hierarchy', 'featured')
    prepopulated_fields = {'slug': ('name',)}


class HierarchyAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug',
            )
        }),
    )
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Hierarchy, HierarchyAdmin)
