from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from stark.utils.page import Pagination
from django.conf.urls import url
from django.urls import reverse


# 分页类
class ShowList(object):

    # 初始化数据
    def __init__(self, config_obj, queryset, request):
        self.config_obj = config_obj
        self.queryset = queryset
        self.request = request

        # 分页
        current_page = self.request.GET.get('page')
        pagination = Pagination(current_page, self.queryset.count(), self.request.GET, per_page_num=2)
        self.pagination = pagination
        self.page_queryset = self.queryset[self.pagination.start:self.pagination.end]

    # 表头
    def get_header(self):
        header_list = []
        for field_or_func in self.config_obj.get_new_list_display():
            if isinstance(field_or_func, str):

                if field_or_func == '__str__':
                    val = self.config_obj.model._meta.model_name.upper()
                else:
                    field_obj = self.config_obj.model._meta.get_field(field_or_func)
                    val = field_obj.verbose_name
            else:
                val = field_or_func(self.config_obj, is_header=True)

            header_list.append(val)
        return header_list

    # 表单数据
    def get_body(self):
        data_list = []
        for obj in self.page_queryset:
            temp = []
            for field_or_func in self.config_obj.get_new_list_display():
                if isinstance(field_or_func, str):
                    val = getattr(obj, field_or_func)
                    if field_or_func in self.config_obj.list_display_links:
                        val = mark_safe("<a href= '%s'>%s</a>" % (self.config_obj.get_reverse_url('change', obj), val))
                else:
                    val = field_or_func(self.config_obj, obj)

                temp.append(val)

            data_list.append(temp)
        return data_list


# 配置类对象
class ModelStark():
    def __init__(self, model):
        self.model = model
        self.model_name = self.model._meta.model_name
        self.app_label = self.model._meta.app_label
        self.app_model_name = (self.app_label, self.model_name)

    list_display = ['__str__']
    list_display_links = []
    model_form_class = []

    # 反向解析出urls
    def get_reverse_url(self, type, obj=None):
        url_name = '%s_%s_%s' % (self.app_label, self.model_name, type)
        if obj:
            _url = reverse(url_name, args=(obj.pk,))
        else:
            _url = reverse(url_name)
        return _url

    # 删除
    def delete_col(self, obj=None, is_header=False):
        if is_header:
            return '删除'
        return mark_safe("<a href='%s'>删除</a>" % self.get_reverse_url('delete', obj))

    # 修改
    def edit_col(self, obj=None, is_header=False):
        if is_header:
            return '编辑'
        return mark_safe("<a href='%s'>编辑</a>" % self.get_reverse_url('change', obj))

    # 复选框
    def check_col(self, obj=None, is_header=False):
        if is_header:
            return '选择'
        return mark_safe("<input type='checkbox'>")

    # 添加数据列
    def get_new_list_display(self):
        new_list_display = []

        new_list_display.extend(self.list_display)
        if not self.list_display_links:
            new_list_display.append(ModelStark.edit_col)
        new_list_display.append(ModelStark.delete_col)
        new_list_display.insert(0, ModelStark.check_col)

        return new_list_display

    # 查看数据
    def list_view(self, request):
        """ 1
         data_list = [
            ['三国演义', 122],
            ['西游记', 13],
            ['金瓶梅', 45]
        ]
        :param request:
        :return:
        """
        queryset = self.model.objects.all()
        show_list = ShowList(self, queryset, request)

        # 获取添加url发送给前端页面
        add_url = self.get_reverse_url("add")

        return render(request, 'stark/list_view.html', locals())

    # =================================>

    # 定义form类
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        else:
            from django import forms

            class ModelFormDemo(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"

            return ModelFormDemo

    # 添加
    def add_view(self, request):

        from django import forms

        class ModelFormAdd(forms.ModelForm):
            class Meta:
                model = self.model
                fields = '__all__'

        # get请求要拿到一个空的数据
        form = ModelFormAdd()
        if request.method == "POST":
            # post请求返回有数据的页面
            form = ModelFormAdd(request.POST)

            if form.is_valid():
                form.save()

                return redirect(self.get_reverse_url('list'))

        return render(request, 'stark/add_view.html', locals())

        # if request.method == 'GET':
        #     form = form = ModelFormAdd()
        #     return render(request, "stark/add_view.html", locals())
        # else:
        #     form = ModelFormAdd(request.POST)
        #     if form.is_valid():
        #         form.save()
        #         return redirect(self.get_reverse_url("list"))
        #     else:
        #         return render(request, "stark/add_view.html", locals())

    # 修改
    def change_view(self, request, id):
        from django import forms
        # if request.method == "POST":
        #     edit_obj = self.model.objects.get(pk=id)
        #
        # return render(request, 'stark/change_view.html', locals())

        ModelFormChange = self.get_model_form_class()
        edit_obj = self.model.objects.get(pk=id)
        if request.method == "GET":

            form = ModelFormChange(instance=edit_obj)
            return render(request, "stark/change_view.html", locals())
        else:
            form = ModelFormChange(data=request.POST, instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_reverse_url("list"))
            else:
                return render(request, "stark/change_view.html", locals())

    # 删除
    def delete_view(self, request, id):
        if request.method == "POST":
            self.model.objects.get(pk=id).delete()
            return redirect(self.get_reverse_url("list"))

        list_url = self.get_reverse_url("list")
        return render(request, "stark/delete_view.html", locals())

    # 获取urls值
    def get_urls(self):
        temp = [
            url("^$", self.list_view, name="%s_%s_list" % (self.app_model_name)),
            url("^add/$", self.add_view, name='%s_%s_add' % (self.app_model_name)),
            url("^(\d+)/change/$", self.change_view, name='%s_%s_change' % (self.app_model_name)),
            url("^(\d+)/delete$", self.delete_view, name='%s_%s_delete' % (self.app_model_name)),
        ]

        return temp

    # 模仿Django源码返回元组
    @property
    def urls(self):
        return self.get_urls(), None, None


class StarkSite(object):

    def __init__(self, name='admin'):
        self._registry = {}

    def register(self, model, admin_class=None, **options):
        if not admin_class:
            admin_class = ModelStark

        self._registry[model] = admin_class(model)

    def get_urls(self):

        temp = []

        for model_class, config_obj in self._registry.items():
            model_name = model_class._meta.model_name
            app_label = model_class._meta.app_label
            temp.append(url(r'^%s/%s/' % (app_label, model_name), config_obj.urls), )

        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


site = StarkSite()
