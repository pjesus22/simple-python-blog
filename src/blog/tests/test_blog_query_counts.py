from django.urls import reverse


class PostQueryCountTests:
    def test_public_list_query_count(
        self, client, published, django_assert_num_queries
    ):
        with django_assert_num_queries(2):
            assert client.get(reverse("post-list")).status_code == 200

    def test_detail_query_count(self, client, published, django_assert_num_queries):
        url = reverse("post-detail", args=[published.slug])
        with django_assert_num_queries(1):
            assert client.get(url).status_code == 200

    def test_authenticated_filtered_list_query_count(
        self, client, user_factory, published, django_assert_num_queries
    ):
        client.force_login(user_factory())
        with django_assert_num_queries(4):
            resp = client.get(
                reverse("post-list"), {"category": published.category.slug}
            )
            assert resp.status_code == 200

    def test_category_list_query_count(
        self, client, category_factory, django_assert_num_queries
    ):
        category_factory()
        with django_assert_num_queries(2):
            assert client.get(reverse("category-list")).status_code == 200
