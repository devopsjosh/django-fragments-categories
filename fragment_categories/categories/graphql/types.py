from graphene_django import DjangoObjectType
from graphene import relay

from fragment_categories.categories.models import Category, Hierarchy

class CategoryHierarchyNode(DjangoObjectType):
    class Meta:
        model = Hierarchy

        filter_fields = {
            'name': ['exact', 'icontains'],
            'slug': ['exact', ],
        }
        interfaces = (relay.Node,)

class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category

        filter_fields = {
            'name': ['exact', 'icontains'],
            'slug': ['exact', ],
        }
        interfaces = (relay.Node,)
