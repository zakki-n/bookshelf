from django.db import models
from django.contrib.auth import get_user_model
from .consts import MAX_RATE

RATE_CHOICES = [(x, str(x)) for x in range(0, MAX_RATE + 1)]

CATEGORY = (
    ('business', 'ビジネス'),
    ('life', '生活'),
    ('hobby', '趣味'),
    ('other', 'その他'),
)

class Shelf(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    thumbnail = models.ImageField(null=True, blank=True)
    category = models.CharField(
        max_length=100,
        choices = CATEGORY,
        )
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.title
class Review(models.Model):
    book = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    rate = models.IntegerField(choices=RATE_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 同じユーザーが同じ本を複数回お気に入り登録できないようにする
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} likes {self.book.title}'
