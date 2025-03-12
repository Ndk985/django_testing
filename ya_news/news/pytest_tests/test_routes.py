import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_access(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_page_access(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200
    assert news.title.encode() in response.content
    assert news.text.encode() in response.content


@pytest.mark.django_db
def test_comment_edit_and_delete_pages_access_to_author(
    client, author, comment
):
    client.force_login(author)
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})

    edit_response = client.get(edit_url)
    delete_response = client.get(delete_url)

    assert edit_response.status_code == 200
    assert delete_response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_and_delete_pages_redirect_anonymous_to_login(
    client, comment
):
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})

    edit_response = client.get(edit_url)
    delete_response = client.get(delete_url)

    assert edit_response.status_code == 302
    assert delete_response.status_code == 302

    login_url = reverse('users:login')
    assert edit_response.url.startswith(login_url)
    assert delete_response.url.startswith(login_url)


@pytest.mark.django_db
def test_comment_edit_and_delete_pages_restricted_to_other_users(
    client, other_user, comment
):
    client.force_login(other_user)
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})

    edit_response = client.get(edit_url)
    delete_response = client.get(delete_url)

    assert edit_response.status_code == 404
    assert delete_response.status_code == 404


@pytest.mark.django_db
def test_auth_pages_access_to_anonymous(client):
    signup_url = reverse('users:signup')
    login_url = reverse('users:login')
    logout_url = reverse('users:logout')

    signup_response = client.get(signup_url)
    login_response = client.get(login_url)
    logout_response = client.get(logout_url)

    assert signup_response.status_code == 200
    assert login_response.status_code == 200
    assert logout_response.status_code == 200
