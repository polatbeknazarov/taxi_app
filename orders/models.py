from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Order(models.Model):
    address = models.TextField()
    in_search = models.BooleanField(default=True)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.driver)
