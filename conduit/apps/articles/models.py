from django.db import models

from conduit.apps.core.models import TimestampedModel
from django_extensions.db.models import AutoSlugField


class Article(TimestampedModel):
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    title = models.CharField(db_index=True, max_length=255)

    description = models.TextField()
    body = models.TextField()

    # Every article must have an author. This will answer questions like "Who
    # gets credit for writing this article?" and "Who can edit this article?".
    # Unlike the `User` <-> `Profile` relationship, this is a simple foreign
    # key (or one-to-many) relationship. In this case, one `Profile` can have
    # many `Article`s.
    author = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='articles'
    )

    # An article should belong to a Category. A many-to-one relationship
    # thus a category can have many articles
    category = models.ForeignKey(
        'articles.Category', related_name='articles', blank=True, null=True)

    tags = models.ManyToManyField(
        'articles.Tag', related_name='articles'
    )

    def __str__(self):
        return self.title


"""
A category can belong to another and it too can belong to anothor.
"""


class Category(TimestampedModel):
    name = models.CharField(db_index=True, max_length=150, unique=True)
    # Unique slug field to enforce that categories are the same as lone categories or subcategory
    # A concatenation of the supercategory(if specified) and its name
    slug = AutoSlugField(populate_from=['supercategory', 'name'], unique=True)

    # A one-to-many relation where a category can belong to another category(supercategory) as a subcategory
    supercategory = models.ForeignKey(
        'self', related_name='subcategories', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        # unique_together = ('name', 'supercategory')
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Comment(TimestampedModel):
    body = models.TextField()

    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'profiles.Profile', related_name='comments', on_delete=models.CASCADE
    )


class Tag(TimestampedModel):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.tag
