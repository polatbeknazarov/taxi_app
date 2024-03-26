from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Line(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.driver)
