from django.db import models
from django.contrib.auth.models import User

class Deck(models.Model):
    user = models.ForeignKey(               
        User,
        on_delete=models.CASCADE,
        related_name='decks',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def card_count(self):
        return self.cards.count()


class Flashcard(models.Model):
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='cards'
    )

    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Q: {self.question[:60]}"

    
class Note(models.Model):
    User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    original_text = models.TextField()
    summary = models.TextField(blank=True)
    key_points = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    def key_points_list(self):
        if not self.key_points:
            return []
        return [
            point.lstrip('.').strip()
            for point in self.key_points.split('\n')
            if point.strip()
        ]


