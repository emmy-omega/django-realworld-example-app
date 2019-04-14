from django.test import TestCase
from .models import Category, Article
from ..authentication.models import User

from .views import CategoryViewSet, ArticleViewSet
from .models import Category, Article
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status


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


"""
    This class defines the test suite for the Cetgory Views.
    DRF's reverse used to form urls instead of hard-coding them
    """


class CategoryViewTestCase(APITestCase):
    def setUp(self):
        """
        setup a requestFactory to test the  views directly and
        viewset to be the Category
        """
        self.factory = APIRequestFactory()
        self.viewset = CategoryViewSet

        # create a user for testing for authorisation and required field purposes
        self.user = User.objects.create(username='testUser')

        # create a category
        self.category = Category.objects.create(name='sports')

        # setup the slug url keyword argument to be used request formation
        self.kwargs = {'slug': 'sports'}
        return super().setUp()

    """
    Test then category's list view 
    """

    def test_category_list(self):
        # Test category list
        uri = reverse('articles:category-list')
        view = self.viewset.as_view({'get': 'list', 'post': 'create'})
        request = self.factory.get(uri)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test category create
        request = self.factory.post(
            uri, {"category": {"name": "test category"}}, format='json')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response.render()
        self.assertJSONEqual(
            response.content, {"category": {"name": "test category", "slug": "test-category"}})

    """
    Test category'a detail view
    """

    def test_category_detail(self):
        uri = reverse('articles:category-detail', args=[self.category.slug])
        view = self.viewset.as_view({'put': 'update', 'delete': 'destroy'})
        # Test category update
        request = self.factory.put(
            uri, {"name": "sportify"}, format='json')
        force_authenticate(request, user=self.user)
        response = view(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        self.assertJSONEqual(response.content, {"category": {
                             "name": "sportify", "slug": "sports"}})

        # Test category delete
        request = self.factory.delete(uri)
        force_authenticate(request, user=self.user)
        response = view(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    """
    Test category's articles view
    Should returns the articles belong to the specified category
    """

    def test_category_article_list(self):
        self.category.articles.create(
            title='test title', author=self.user.profile, category=self.category)
        # kwargs = {'slug': self.category.slug}
        uri = reverse('articles:category-articles', kwargs=self.kwargs)
        request = self.factory.get(uri)
        view = self.viewset.as_view({'get': 'articles'})
        response = view(request, **self.kwargs)
        response.render()
        self.assertEqual(response.data.popitem(False)[1], 1)

    """
    Test category's article view
    Should create an artile with the specified category as it's own
    """

    def test_category_article_create_url(self):
        uri = reverse('articles:category-article', kwargs=self.kwargs)
        data = {"article": {"title": "test title", "body": "test body"}}
        request = self.factory.post(uri, data, format='json')
        view = self.viewset.as_view({'post': 'articles'})
        # force authicate request as it should requires authorization
        force_authenticate(request, user=self.user)
        response = view(request, **self.kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    """
    Test article's list view
    Should return list of articles belonging to the category specified in the category query param
    """

    def test_param_filtered_articles(self):
        Article.objects.create(title='test article 1',
                               author=self.user.profile, category=self.category)
        alt_category = Category.objects.create(name='altCategory')
        Article.objects.create(title='test article 2',
                               author=self.user.profile, category=alt_category)
        uri = reverse('articles:article-list')
        request = self.factory.get(uri, {"category": "sports"})
        view = ArticleViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.popitem(False)[1], 1)
