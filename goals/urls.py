
from django.urls import path

from goals.views import GoalCategoryCreateView, GoalCategoryListView, GoalCategoryView, GoalCreateView, GoalListView, \
    GoalView, GoalCommentCreateView, GoalCommentListView, GoalCommentView

urlpatterns = [
    path('goal_category/create', GoalCategoryCreateView.as_view(), name='create-category'),
    path('goal_category/list', GoalCategoryListView.as_view(), name='category-list'),
    path('goal_category/<pk>', GoalCategoryView.as_view(), name='category-retrieve'),

    path('goal/create', GoalCreateView.as_view(), name='create-goal'),
    path('goal/list', GoalListView.as_view(), name='list-goals'),
    path('goal/<pk>', GoalView.as_view(), name='retrieve-update-destroy-goal'),

    path('goal_comment/create', GoalCommentCreateView.as_view(), name='create-comment'),
    path('goal_comment/list', GoalCommentListView.as_view(), name='list-comment'),
    path('goal_comment/<pk>', GoalCommentView.as_view(), name='retrieve-update-destroy-comment'),
]
