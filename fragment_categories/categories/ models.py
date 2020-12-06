import re
import operator
from django.db import models
from django.utils.text import slugify
from django.core.urlresolvers import reverse

class Hierarchy(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'hierarchies'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ellington_categories_hierarchy', args=[self.slug])
        return "/categories/%s/" % self.slug

    def get_category_from_slug(self, slug_path, raise404=False):
        """
        Return a category given a hierarchical URL peice.
        """
        lookup = {
            'hierarchy__pk': self.id,
            'slug_path__exact': slug_path,
        }
        if raise404:
            from django.shortcuts import get_object_or_404
            return get_object_or_404(Category, **lookup)
        else:
            return Category.objects.get(**lookup)

    def get_all_categories(self):
        return list(self.categories.all())

    def get_toplevel_categories(self):
        return self.categories.filter(parent__isnull=True)

    def get_toplevel_category_list(self):
        return list(self.get_toplevel_categories())

    def get_toplevel_category_count(self):
        return self.get_toplevel_categories().count()


class CategoryManager(models.Manager):
    def rebuild(self):
        for cat in self.get_query_set().all():
            cat.slugify()

        for cat in self.get_query_set().filter(parent__isnull=True):
            cat.refresh_paths(force=True)

    def get_all_for_list(self, category_list):
        """
        Given a list of Category objects, this returns a list of all the Categories
        plus all the Categories' children, plus the childrens' children, etc.
        For example, if the "Arts" Category is passed as a parameter, this function
        will return ["Arts", "Arts/Music", "Arts/Music/Local" ...]
        """
        if not category_list:
            return []
        qs = reduce(operator.or_, (models.Q(path__startswith=c.path) for c in category_list))
        return self.filter(qs).order_by('path')

    def get_recursive_paths(self, path):
        bits = get_path_bits(path)
        result = []
        for i, bit in enumerate(bits):
            result.append('/%s' % '/'.join(bits[:i+1]))
        return result

    def get_path_bits(path):
        return [bit.strip() for bit in path.strip().strip('/').split('/')]


class Category(models.Model):
    hierarchy = models.ForeignKey(
        Hierarchy,
        blank=True,
        related_name="categories",
        help_text="Must be explicitly selected if there is no parent category.",
        null=True
    )

    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name="children",
        help_text="If not defined, this will be a top-level category in the given hierarchy.",
        verbose_name='Parent'
    )
    name = models.CharField(
        max_length=100
    )
    slug = models.SlugField()
    path = models.CharField(
        max_length=300, blank=True, editable=False, db_index=True
    )
    slug_path = models.CharField(
        max_length=300, blank=True, editable=False, db_index=True
    )
    featured = models.BooleanField(default=False)
    objects = CategoryManager()
    
    
    class Meta:
        verbose_name_plural = 'categories'
        unique_together = (('parent', 'name'),)
        ordering = ('path',)

    def __str__(self):
        return '[%s] %s' % (self.hierarchy.name, self.path)

    def get_absolute_url(self):
        return reverse(
            'core_category',
            kwargs={'slug': self.hierarchy.slug, 'category_slug': self.slug})

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        self.refresh_paths()

    def refresh_paths(self, force=False):
        """
        Determines this Category's path by looking at its name and
        the paths of its parents. If it's changed, it's saved.
        """
        if self.parent_id is None:
            path = '/%s' % self.name
        else:
            parent = self.parent
            path = '%s/%s' % (parent.path, self.name)
        slug_path = slugify_path(path)
        if force or path != self.path or slug_path != self.slug_path:
            self.path = path
            self.slug_path = slug_path
            self.save()
            changed = True
        else:
            changed = False
        if changed:
            for child in self.get_children():
                child.refresh_paths()

    def get_children(self):
        "Returns a list of Category objects that are children -- only one level deep."
        if not hasattr(self, '_children'):
            self._children = list(self.children.all())
        return self._children

    def get_all_children(self, **kwargs):
        "Returns a list of Category objects that are children -- all children."
        kwargs['hierarchy__id__exact'] = self.hierarchy_id
        kwargs['path__startswith'] = self.path + '/'
        return Category.objects.filter(**kwargs)

    def get_parents(self):
        if not hasattr(self, '_parents'):
            self._parents = []
            current = self
            while current.parent_id:
                current = current.parent
                self._parents.insert(0, current)
        return self._parents


def slugify(slug):
    slug = slug.strip().lower()
    slug = re.sub(r'[^a-z0-9 ]', '', slug)
    slug = re.sub(r' +', '-', slug)
    return slug


def get_path_bits(path):
    return [bit.strip() for bit in path.strip().strip('/').split('/')]


def slugify_path(path):
    return '/%s' % '/'.join([slugify(bit) for bit in get_path_bits(path)])



class CategoryModel(models.Model):
    categories = models.ManyToManyField(
        Category,
        blank=True
    )

    class Meta:
        abstract = True