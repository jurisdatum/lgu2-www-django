
# from django.db import models

# class Message(models.Model):
#     name = models.CharField(max_length=255, unique=True)
#     text = models.TextField()

#     def __str__(self):
#         return self.name


# class DatasetCompleteness(models.Model):
#     type = models.CharField(max_length=5, blank=False, unique=True, choices=[('ukpga', 'ukpga')])
#     cutoff = models.PositiveSmallIntegerField(blank=False, null=True, help_text='first complete year')

#     def __str__(self):
#         return self.type

#     class Meta:
#         verbose_name = 'Dataset Completeness'
#         verbose_name_plural = 'Dataset Completeness'
