from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListBookView.as_view(), name='list-book'),
    path('book/<int:pk>/detail/', views.DetailBookView.as_view(), name='detail-book'),
    path('book/create/', views.CreateBookView.as_view(), name='create-book'),
    path('book/<int:pk>/delete/', views.DeleteBookView.as_view(), name='delete-book'),
    path('book/<int:pk>/update/', views.UpdateBookView.as_view(), name='update-book'),
    path('book/<int:book_id>/review/', views.CreateReviewView.as_view(), name='review'),
    path('book/search/', views.SearchBookView.as_view(), name='search-book'),
    path('book/<int:pk>/add_favorite/', views.AddFavoriteView.as_view(), name='add-favorite'),
    path('book/<int:pk>/delete_favorite/', views.DeleteFavoriteView.as_view(), name='delete-favorite'),
    path('favorite/', views.FavoriteListView.as_view(), name='favorite-list'),
]