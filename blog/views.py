from django.shortcuts import render
from django.views import View
from .models import BlogPost

class BlogHomePageView(View):
    template_name = "blog/home.html"
    def get(self, request, *args, **kwargs):
        blogs = BlogPost.objects.all()
        return render(request, self.template_name, {
            "blogs": blogs,
            })

class BlogPostView(View):
    template_name = "blog/blog_post.html"
    def get(self, request, *args, **kwargs):
        blog = BlogPost.objects.get(pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {
            "blog": blog,
            })