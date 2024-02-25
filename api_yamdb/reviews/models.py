from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(max_length=256)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        self.rating = self.reviews.aggregate(
            avg_score=models.Avg('score'))['avg_score']
        self.save()

    class Meta:
        unique_together = ['author', 'title']
        verbose_name = 'Отзыв'

    def __str__(self):
        return self.title


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=256)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'

    def __str__(self):
        return self.review
