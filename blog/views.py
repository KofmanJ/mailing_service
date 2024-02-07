# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from blog.models import Blog


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ('title', 'content', 'preview', )
    success_url = reverse_lazy('blog:blog_list')


class BlogListView(ListView):
    model = Blog
    fields = ('title', 'content', 'preview', 'public_date', )

    # def get_queryset(self, *args, **kwargs):  # Выводит в список статей только c положительным признаком публикации
    #     queryset = super().get_queryset(*args, **kwargs)
    #     queryset = queryset.filter(public_date=True)
    #     return queryset


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ('title', 'content', 'preview', )

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
