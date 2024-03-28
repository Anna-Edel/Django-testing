import pytest
from model_bakery import baker
from students.models import Course, Student
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_cource(client, course_factory):
    # проверка получения одного курса
    # Arrange
    courses = course_factory()
    print(courses.id, courses.name)

    # Act
    response = client.get(f'/api/v1/courses/{courses.id}/')
    print(response)
    # Assert
    data = response.json()
    assert response.status_code == 200
    assert courses.name == data['name']

@pytest.mark.django_db
def test_get_cources(client, course_factory):
    # проверка получения списка курсов
    # Arrange
    quantity = 999
    courses = course_factory(_quantity=quantity)

    # Act
    response = client.get('/api/v1/courses/')

    # Assert проверяем код возврата, количество и имена всех созданных курсов
    data = response.json()
    assert response.status_code == 200
    assert len(data) == quantity
    for i, course in enumerate(data):
        assert courses[i].name == course['name']


@pytest.mark.django_db
#проверка фильтрации списка курсов по id:
@pytest.mark.django_db
def test_filter_courses_id(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    #Act
    response = client.get('/api/v1/courses/', {'id': courses[5].id})
    #Assert
    data = response.json()
    assert data[0]['id'] == courses[5].id
    assert data[0]['name'] == courses[5].name


#проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_filter_courses_name(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    #Act
    response = client.get('/api/v1/courses/', {'name': courses[3].name})
    #Assert
    data = response.json()
    assert data[0]['name'] == courses[3].name
    

@pytest.mark.django_db
def test_create_course(client):
    # тест успешного создания курса
    # Arrange
    count = Course.objects.count()
    name = 'Python from zero'
    # Act
    response1 = client.post('/api/v1/courses/', data={'name': name})
    response2 = client.get(f'/api/v1/courses/?name={name}')
    response3 = client.get(f'/api/v1/courses/{response1.json()["id"]}/')
    # Assert
    assert response1.status_code == 201
    assert Course.objects.count() == count + 1
    assert response2.status_code == 200
    assert name == response3.json()['name']


#тест успешного обновления курса
@pytest.mark.django_db
def test_update_course(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    course_update = {'name': 'Django'}
    #Act
    response = client.patch(f'/api/v1/courses/{courses[3].id}/', data=course_update, format='json')
    #Assert
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == course_update['name']
    # print(data['name']) #для вывода на печать использовать команду pytest -s


#тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    count = Course.objects.count()
    course_deleted = courses[3].id
    #Act
    response = client.delete(f'/api/v1/courses/{courses[3].id}/')
    #Assert
    assert response.status_code == 204
    assert Course.objects.count() == count - 1
    assert not Course.objects.filter(id=course_deleted).exists()
    response_deleted = client.get(f'/api/v1/courses/{course_deleted}/')
    assert response_deleted.status_code == 404
