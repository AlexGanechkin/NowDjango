# Данные вьюхи написаны до 29 урока по DRF, чтобы работали скопируй код во views

import json

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView

from nowdjango import settings
from vacancies.models import Vacancy, Skill
from vacancies.serializers import VacancyDetailSerializer, VacancyListSerializer, VacancyCreateSerializer


def hello(request):
    return HttpResponse("Hello world")


@method_decorator(csrf_exempt, name="dispatch")
class VacancyListView(ListView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        search_text = request.GET.get("text", None)
        if search_text:
            self.object_list = self.object_list.filter(text=search_text)

        """ Сортировка """

        # self.object_list = self.object_list.order_by("text", "slug")  # "-text" - обратный порядок

        """ JOIN запросы """
        # select_related - для ForeignKey-связи
        # prefetch_related - для M2M-связи
        self.object_list = self.object_list.select_related('user').prefetch_related('skills').order_by("text", "slug")

        """ Пагинация
        1 - 0:10
        2 - 10:20
        3 - 20:30

        total = self.object_list.count()
        page_number = int(request.GET.get("page", 1))
        offset = (page_number - 1) * settings.TOTAL_ON_PAGE
        if offset < total:
            self.object_list = self.object_list[offset:offset + settings.TOTAL_ON_PAGE]
        else:
            self.object_list = self.object_list[offset:offset + total]
        """
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # vacancies = []
        # for vacancy in page_obj:
        #     vacancies.append({
        #         "id": vacancy.id,
        #         "text": vacancy.text,
        #         "username": vacancy.user.username, # для этого нужен select_related
        #         "skills": list(map(str, vacancy.skills.all()))
        #     })
        list(map(lambda x: setattr(x, "username", x.user.username if x.user else None), page_obj))

        response = {
            "items": VacancyListSerializer(page_obj, many=True).data,
            "num_pages": paginator.num_pages,
            "total": paginator.count
        }

        return JsonResponse(response, safe=False)


class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        # vacancy = self.get_object()

        return JsonResponse(VacancyDetailSerializer(self.object).data)
        # try:
        #    vacancy = self.get_object()
        # except Vacancy.DoesNotExist:
        #    return JsonResponse({"error": "Not found"}, status=404)

        # return JsonResponse({
        #     "id": self.object.id,
        #     "text": self.object.text,
        #     "slug": self.object.slug,
        #     "status": self.object.status,
        #     "created": self.object.created,
        #     "user": self.object.user_id,
        #     "skills": list(self.object.skills.all().values_list("name", flat=True)),
        #     #"skills 2": [{"name": skill} for skill in list(self.object.skills.all().values_list("name", flat=True))],
        #     #"skills 3": list(map(str, self.object.skills.all()))
        # }, safe=False, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name="dispatch")
class VacancyCreateView(CreateView):
    model = Vacancy
    fields = ['id', 'user', 'slug', 'text', 'status', 'created', 'skills']

    def post(self, request, *args, **kwargs):
        vacancy_data = VacancyCreateSerializer(data=json.loads(request.body))
        if vacancy_data.is_valid():
            vacancy_data.save()
        else:
            JsonResponse(vacancy_data.errors)

        return JsonResponse(vacancy_data.data)

        # vacancy = Vacancy.objects.create(
        #     user_id=vacancy_data['user_id'],
        #     slug=vacancy_data['slug'],
        #     text=vacancy_data['text'],
        #     status=vacancy_data['status'],
        # )

        # vacancy.user = get_object_or_404(User, pk=vacancy_data['user'])
        # """ Можно так...
        # review_data = json.loads(request.body)
        # review = Review()
        # review.author = review_data['author']
        # review.content = review_data['content']
        # review.rate = review_data['rate']
        # review.is_published = review_data['is_published']
        # review.tour = get_object_or_404(Tour, pk=review_data["tour_id"])
        # review.save()
        # """

        # for skill in vacancy_data['skills']:
        #    skill_obj, created = Skill.objects.get_or_create(name=skill, defaults={"is_active": True})
        #    """
        #    try:
        #        skill_obj = Skill.objects.get(name=skill)
        #    except Skill.DoesNotExist:
        #        skill_obj = Skill.objects.create(name=skill)
        #    """
        #     vacancy.skills.add(skill_obj)
        # vacancy.save()

        # return JsonResponse({
        #    "id": vacancy.id,
        #    "text": vacancy.text
        # })


@method_decorator(csrf_exempt, name="dispatch")
class VacancyUpdateView(UpdateView):
    model = Vacancy
    fields = ['slug', 'text', 'status', 'skills']

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        vacancy_data = json.loads(request.body)
        self.object.slug = vacancy_data['slug']
        self.object.text = vacancy_data['text']
        self.object.status = vacancy_data['status']

        for skill in vacancy_data['skills']:
            try:
                skill_obj = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return JsonResponse({"error": "Skill not found"}, status=404)
            self.object.skills.add(skill_obj)

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "text": self.object.text,
            "slug": self.object.slug,
            "status": self.object.status,
            "created": self.object.created,
            "user": self.object.user_id,
            "skills": list(self.object.skills.all().values_list("name", flat=True)),
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyDeleteView(DeleteView):
    model = Vacancy
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "deleted"}, status=200)


class USerVacancyDetailView(View):
    def get(self, request):
        user_qs = User.objects.annotate(vacancies=Count('vacancy'))

        paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        users = []
        for user in page_obj:
            users.append({
                "id": user.id,
                "name": user.username,
                "vacancies": user.vacancies
            })

        response = {
            "items": users,
            "total": paginator.count,
            "num_pages": paginator.num_pages,
            "avg": user_qs.aggregate(Avg('vacancies'))  # просто число: (avg=Avg('vacancies'))['avg']
        }

        return JsonResponse(response)
