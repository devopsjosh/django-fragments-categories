from django import forms
from .models import Category


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['hierarchy', 'parent', 'name', 'slug', 'featured']

    required_if_other_not_given = {
        'hierarchy': 'parent',
        'parent': 'hierarchy',
    }

    def clean_name(self):
        if '/' in self.cleaned_data['name']:
            raise forms.ValidationError(
                "A category name can't contain slashes.")
        return self.cleaned_data['name']

    def clean(self):
        super(CategoryAdminForm, self).clean()

        if 'slug' in self.cleaned_data and 'parent' in self.cleaned_data and 'hierarchy' in self.cleaned_data:
            if self.cleaned_data['parent'] is not None:
                self.cleaned_data['hierarchy'] = self.cleaned_data['parent'].hierarchy

            kwargs = {}
            if self.cleaned_data.get('hierarchy', False):
                kwargs['hierarchy__pk'] = int(
                    self.cleaned_data['hierarchy'].id)
                kwargs['parent__isnull'] = True
            else:
                kwargs['parent__pk'] = int(self.cleaned_data['parent'].id)
            this_level_slugs = [c.slug for c in Category.objects.filter(
                **kwargs) if c.id != self.initial.get("id", None) and c.id != self.instance.id]
            if self.cleaned_data['slug'] in this_level_slugs:
                raise forms.ValidationError(
                    "A category slug must be unique among categories at its level.")

            if not self.cleaned_data['parent']:
                return self.cleaned_data

            p_data = int(self.cleaned_data['parent'].pk)
            h_data = self.cleaned_data.get('hierarchy', False)
            if h_data:
                h_data = int(h_data.pk)
            if p_data and h_data:
                p = Category.objects.get(pk=p_data)
                if p.hierarchy_id != h_data:
                    raise forms.ValidationError(
                        "This parent is not within the selected hierarchy.")

            this_id = self.cleaned_data.get("id", None)
            if not this_id:
                return self.cleaned_data

            try:
                selected_parent = Category.objects.get(pk=p_data)
            except Category.DoesNotExist:
                return self.cleaned_data

            if selected_parent.id == this_id:
                raise forms.ValidationError(
                    "A category can't be its own parent.")

            try:
                this_category = Category.objects.get(pk=p_data)
            except Category.DoesNotExist:
                return self.cleaned_data

            for c in this_category.get_all_children():
                if c.id == this_id:
                    raise forms.ValidationError(
                        "A category can't set a child category to be its own parent.")
            return self.cleaned_data
        else:
            raise forms.ValidationError("Cannot clean data")
