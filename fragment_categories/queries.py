import graphene
from graphene_django.filter import DjangoFilterConnectionField

from .types import CategoryHierarchyNode, CategoryNode


class Query(graphene.ObjectType):
    category = graphene.relay.Node.Field(
        CategoryNode, description="Queries a single category.")
    categories = DjangoFilterConnectionField(
        CategoryNode, description="Queries a paginated list of categories.")

    category_hierarchy = graphene.relay.Node.Field(
        CategoryHierarchyNode, description="Queries a single category hierarchy.")
    category_hierarchies = DjangoFilterConnectionField(
        CategoryHierarchyNode, description="Queries a paginated list of category hierarchies.")
