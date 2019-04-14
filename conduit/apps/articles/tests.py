from django.test import TestCase
from .models import Category, Article
from ..authentication.models import User


class CategoryModelTestCase(TestCase):
    """
    This class defines the test suite for the Cetgory model.
    """

    def setUp(self):
        # Setup a user to be used author definition in artilces
        self.user = User.objects.create(username='testUser')
        # Base category to referenced in the tests
        self.category = Category.objects.create(name='TestCase')
        return super().setUp()

    """
    Test Category's self relationship i.e A category may belong to another which in turn belongs to another
    Test Category's slug properties concatenation of its super's and it's name i.e super_name-category_name
    """

    def test_supercategory(self):
        subcategory = Category(name="Test",
                               supercategory=self.category)
        subcategory.save()
        self.assertEqual(subcategory.supercategory, self.category)
        self.assertEqual(subcategory.slug,
                         f'{self.category.name}-{subcategory.name}'.lower(), "Subcategory's slug should be testcase-test")

    """
    Test Category's Article relationship 
    i.e Articles belong to Categories
    """

    def test_articles_relation(self):
        test_article = Article.objects.create(
            title='test title', author=self.user.profile, category=self.category)
        self.assertEqual(test_article.category.name, self.category.name,
                         "New article should belong to specified category")
        self.assertEqual(self.category.articles.count(), 1,
                         "Category should have the new artcle")
