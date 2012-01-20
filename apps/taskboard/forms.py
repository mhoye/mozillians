from django import forms
from django.contrib.auth.models import User

from groups.forms import GroupField
from happyforms import ModelForm
from taskboard.models import Task


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class TaskForm(ModelForm):
    contact = UserModelChoiceField(User.objects.all())
    groups = GroupField(required=False)

    class Meta:
        model = Task

    def save(self, commit=True):
        task = super(TaskForm, self).save(commit=False)
        task.save()
        # not using task.save_m2m b/c that would blindly remove
        # system tasks.

        # Remove any non-system groups that weren't supplied in this list.
        task.groups.remove(*[g for g in task.groups.all()
                             if g not in self.cleaned_data['groups']
                             and not g.system])
        # Add any non-system groups from the form
        task.groups.add(*[g for g in self.cleaned_data['groups']
                          if not g.system])
        return task
