from django.urls import include, path

from .views import meal_delivery, employees, admins

urlpatterns = [
    path("", meal_delivery.home, name="home"),
    path("menu/<uuid:pk>/", meal_delivery.MenuDetailView.as_view(), name="menu_detail"),
    path(
        "employees/",
        include(
            (
                [
                    path(
                        "",
                        employees.MealHistoryListView.as_view(),
                        name="meal_history_list",
                    ),
                    path(
                        "menu/<uuid:pk>/",
                        employees.SelectMealView.as_view(),
                        name="select_meal",
                    ),
                ],
                "meal_delivery",
            ),
            namespace="employees",
        ),
    ),
    path(
        "admins/",
        include(
            (
                [
                    path("", admins.MenuListView.as_view(), name="menu_list"),
                    path("menu/add/", admins.MenuCreateView.as_view(), name="menu_add"),
                    path(
                        "menu/<uuid:pk>/",
                        admins.MenuUpdateView.as_view(),
                        name="menu_change",
                    ),
                ],
                "meal_delivery",
            ),
            namespace="admins",
        ),
    ),
]
