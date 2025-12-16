"""Database models for SafePass"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended user model with master password hash"""
    master_password_hash = models.CharField(max_length=256)
    encryption_key_encrypted = models.BinaryField()
    salt = models.BinaryField()
    
    class Meta:
        db_table = 'users'


class PasswordCard(models.Model):
    """Password card storing encrypted credentials"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    app_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password_encrypted = models.BinaryField()
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'password_cards'
    
    def __str__(self):
        return f"{self.app_name} - {self.username}"
