from django.shortcuts import render
from django.views import generic
from django.urls import reverse, reverse_lazy
from .models import Shelf, Review, Favorite
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages # メッセージフレームワークをインポート
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Avg
from django.db.models import Q # Qオブジェクトをインポート
from django.core.paginator import Paginator


class ListBookView(generic.ListView):
    template_name = 'book/book_list.html'
    model = Shelf
    context_object_name = 'Shelf'
    queryset = Shelf.objects.all().order_by('-id')  # 登録順（降順）に並べ替え
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # レビュー平均でソートして上位3冊を取得
        ranking_list = (
            Shelf.objects.annotate(avg_rating=Avg('review__rate')).order_by('-avg_rating')[:3]
        )
        context['ranking_list'] = ranking_list
        return context
    
class DetailBookView(generic.DetailView):
    template_name = 'book/book_detail.html'
    model = Shelf
    context_object_name = 'Shelf'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object() # 現在の本オブジェクトを取得

        # その本のレビューを取得し、ページネーションを適用
        reviews = book.review_set.all().order_by('-id') # 最新のレビューが上に来るように
        paginator = Paginator(reviews, 3) # 1ページに3件表示
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['reviews'] = page_obj

        # ログインしているユーザーがお気に入り登録しているかどうかの情報を追加
        context['is_favorite'] = False
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(user=self.request.user, book=book).exists()

        return context
    
    

class CreateBookView(LoginRequiredMixin, generic.CreateView):
    template_name = 'book/book_create.html'
    model = Shelf
    context_object_name = 'Shelf'
    fields = ('title', 'text', 'category', 'thumbnail')
    success_url = reverse_lazy('list-book')
    def form_valid(self, form):
        form.instance.user = self.request.user  # ログイン中のユーザーを設定
        return super().form_valid(form)

class DeleteBookView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'book/book_confirm_delete.html'
    model = Shelf
    context_object_name = 'Shelf'
    success_url = reverse_lazy('list-book')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied('削除権限がありません。')
        return super(DeleteBookView, self).dispatch(request, *args, **kwargs)
    
class UpdateBookView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'book/book_update.html'
    model = Shelf
    context_object_name = 'Shelf'
    fields = ('title', 'text', 'category', 'thumbnail')
    success_url = reverse_lazy('list-book')
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied('編集権限がありません。')
        return super(UpdateBookView, self).dispatch(request, *args, **kwargs)
    
class CreateReviewView(LoginRequiredMixin, generic.CreateView):
    model = Review
    fields = ('book', 'title', 'text', 'rate')
    template_name = 'book/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Shelf.objects.get(pk=self.kwargs['book_id'])
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detail-book', kwargs={'pk':self.object.book.id})
    
class SearchBookView(generic.ListView):
    template_name = 'book/book_list.html' # 一覧ページと同じテンプレートを再利用
    model = Shelf
    context_object_name = 'Shelf'
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q') # GETパラメータ 'q' から検索クエリを取得

        if query:
            # タイトルまたはテキストに検索クエリが含まれるものをフィルタリング
            # icontains は大文字小文字を区別しない部分一致検索
            # QオブジェクトはOR条件を結合するために使用
            queryset = queryset.filter(Q(title__icontains=query) | Q(text__icontains=query))
        return queryset.order_by('-id') # 登録順（降順）に並べ替え

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # レビュー平均でソートして上位3冊を取得 (ListBookViewと同じロジックを再利用)
        ranking_list = (
            Shelf.objects.annotate(avg_rating=Avg('review__rate')).order_by('-avg_rating')[:3]
        )
        context['ranking_list'] = ranking_list
        context['search_query'] = self.request.GET.get('q', '') # 検索クエリをテンプレートに渡す
        return context
# ここからお気に入り機能のビューを追加
class AddFavoriteView(LoginRequiredMixin, generic.View):
    def post(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Shelf, pk=pk)
        
        # 既にお気に入り登録されているか確認
        if Favorite.objects.filter(user=request.user, book=book).exists():
            messages.warning(request, 'この本は既にお気に入り登録されています。')
        else:
            Favorite.objects.create(user=request.user, book=book)
            messages.success(request, f'{book.title}をお気に入りに追加しました！')
        
        # 詳細ページにリダイレクト
        return redirect('detail-book', pk=pk)

class DeleteFavoriteView(LoginRequiredMixin, generic.View):
    def post(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Shelf, pk=pk)
        
        # お気に入り登録があるか確認して削除
        favorite_obj = Favorite.objects.filter(user=request.user, book=book)
        if favorite_obj.exists():
            favorite_obj.delete()
            messages.info(request, f'{book.title}のお気に入りを解除しました。')
        else:
            messages.warning(request, 'この本はお気に入り登録されていません。')

        # 詳細ページにリダイレクト
        return redirect('detail-book', pk=pk)
class FavoriteListView(LoginRequiredMixin, generic.ListView):
    template_name = 'book/favorite_list.html' # 新しいテンプレートファイルを作成
    model = Favorite # Favoriteモデルを対象とする
    context_object_name = 'favorites' # テンプレートで参照する変数名

    def get_queryset(self):
        # ログインしているユーザーのお気に入り登録を全て取得
        # latest('-created_at') で新しいものから表示
        return Favorite.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 必要であれば、ここで追加のコンテキストデータを渡す
        # 例えば、ユーザーが登録した本の数などを表示する場合
        return context
