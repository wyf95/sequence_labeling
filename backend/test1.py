# -*- coding: utf-8 -*-
# @ModuleName: test
# @Time: 2021/6/10 15:42
# @Author     : WuYaoFei
# @Description:
# @Software   : PyCharm
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# django.setup()

from backend.api.models import Project
from django.shortcuts import get_object_or_404


project = get_object_or_404(Project, pk=2)
# print(project)
