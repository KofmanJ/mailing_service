# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from blog.models import Blog
from blog.forms import BlogForm


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class BlogListView(ListView):
    model = Blog
    fields = ('title', 'content', 'preview', 'public_date', )


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            blog = form.save()
            blog.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:detail', args=[self.kwargs.get('pk')])


class BlogDetailView(LoginRequiredMixin, DetailView):
    model = Blog

    def get(self, request, pk, **kwargs):
        blog = self.get_object()
        context = {
            'object_list': Blog.objects.filter(pk=pk),
        }
        return render(request, 'blog/blog_detail.html', context)

    def get_object(self, queryset=None):
        objects = super().get_object(queryset)
        objects.views_count += 1
        objects.save(update_fields=['views_count'])
        return objects


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog_list')
