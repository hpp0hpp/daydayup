from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.views import generic
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Article, Tag, Category, Timeline, Silian, AboutBlog, Keyword
from .utils import site_full_url
from django.core.cache import cache

from markdown.extensions.toc import TocExtension  # 锚点的拓展
import markdown
import time, os

from haystack.generic_views import SearchView  # 导入搜索视图
from haystack.query import SearchQuerySet
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect, JsonResponse
from .forms import ArticleEditForm

from uuslug import slugify
from django.urls import reverse
import re, uuid


# Create your views here.

def goview(request):
    return render(request, 'test_html.html')


@csrf_exempt
def upload_img(request):
    obj = request.FILES.get('editormd-image-file')
    file_name = time.strftime('%Y%m%d%H%M%S') + str(uuid.uuid1().hex) + '.' + obj.name.split('.')[-1]  # 图片文件名

    f = open(os.path.join(settings.BASE_DIR, 'static', 'blog', 'img', 'article', file_name), 'wb')
    for chunk in obj.chunks():
        f.write(chunk)
    f.close()
    return JsonResponse({"success": 1, "message": "上传成功", "url": "/static/blog/img/article/" + file_name})


class ArchiveView(generic.ListView):
    model = Article
    template_name = 'blog/archive.html'
    context_object_name = 'articles'
    paginate_by = 200
    paginate_orphans = 50

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Article.objects.all()
        else:
            queryset = Article.objects.filter(reviewed=True)
        return queryset


class IndexView(generic.ListView):
    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_ordering(self):
        # ordering = super(IndexView, self).get_ordering()
        sort = self.kwargs.get('sort')
        if sort == 'v':
            return ('-views', '-update_date', '-id')
        return ('-is_top', '-create_date')

    # def get_queryset(self):
    #     queryset = super(IndexView, self).get_queryset()
    #     if not self.request.user.is_superuser:
    #         queryset = queryset.filter(reviewed=True)
    #     return queryset


class DetailView(generic.DetailView):
    model = Article
    template_name = 'blog/detail.html'
    context_object_name = 'article'

    def get_object(self):
        print(self.request.user)
        obj = super(DetailView, self).get_object()
        print(obj)
        # 设置浏览量增加时间判断,同一篇文章两次浏览超过半小时才重新统计阅览量,作者浏览忽略
        u = self.request.user
        ses = self.request.session
        the_key = 'is_read_{}'.format(obj.id)
        is_read_time = ses.get(the_key)
        if u != obj.author:
            if not is_read_time:
                obj.update_views()
                ses[the_key] = time.time()
            else:
                now_time = time.time()
                t = now_time - is_read_time
                if t > 60 * 30:
                    obj.update_views()
                    ses[the_key] = time.time()
        # 获取文章更新的时间，判断是否从缓存中取文章的markdown,可以避免每次都转换
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = '{}_md_{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md:
            obj.body, obj.toc = cache_md
        else:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                TocExtension(slugify=slugify),
            ])
            obj.body = md.convert(obj.body)
            obj.toc = md.toc
            cache.set(md_key, (obj.body, obj.toc), 60 * 60 * 12)
        return obj


class CategoryView(generic.ListView):
    model = Article
    template_name = 'blog/category.html'
    context_object_name = 'articles'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_ordering(self):
        ordering = super(CategoryView, self).get_ordering()
        sort = self.kwargs.get('sort')
        if sort == 'v':
            return ('-views', '-update_date', '-id')
        return ordering

    def get_queryset(self, **kwargs):
        queryset = super(CategoryView, self).get_queryset()
        cate = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        categorynames = list(map(lambda c: c.name, cate.get_sub_categorys()))
        return queryset.filter(category__name__in=categorynames, reviewed=True)

    def get_context_data(self, **kwargs):
        context_data = super(CategoryView, self).get_context_data()
        cate = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        context_data['search_tag'] = '文章分类'
        context_data['search_instance'] = cate
        return context_data


class TagView(generic.ListView):
    model = Article
    template_name = 'blog/tag.html'
    context_object_name = 'articles'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)

    def get_ordering(self):
        ordering = super(TagView, self).get_ordering()
        sort = self.kwargs.get('sort')
        if sort == 'v':
            return ('-views', '-update_date', '-id')
        return ordering

    def get_queryset(self, **kwargs):
        queryset = super(TagView, self).get_queryset()
        tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        return queryset.filter(tags=tag, reviewed=True)

    def get_context_data(self, **kwargs):
        context_data = super(TagView, self).get_context_data()
        tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        context_data['search_tag'] = '文章标签'
        context_data['search_instance'] = tag
        return context_data


def AboutView(request):
    obj = AboutBlog.objects.first()
    if obj:
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = '{}_md_{}'.format(obj.id, ud)
        cache_md = cache.get(md_key)
        if cache_md:
            body = cache_md
        else:
            body = obj.body_to_markdown()
            cache.set(md_key, body, 3600 * 24 * 15)
    else:
        repo_url = 'https://space.bilibili.com/455865239'
        body = '<li>作者 B站 地址：<a href="{}">{}</a></li>'.format(repo_url, repo_url)
    return render(request, 'blog/about.html', context={'body': body})


class TimelineView(generic.ListView):
    model = Timeline
    template_name = 'blog/timeline.html'
    context_object_name = 'timeline_list'


class SilianView(generic.ListView):
    model = Silian
    template_name = 'blog/silian.xml'
    context_object_name = 'badurls'


# 重写搜索视图，可以增加一些额外的参数，且可以重新定义名称
class MySearchView(SearchView):
    context_object_name = 'search_list'
    paginate_by = getattr(settings, 'BASE_PAGE_BY', None)
    paginate_orphans = getattr(settings, 'BASE_ORPHANS', 0)
    queryset = SearchQuerySet().order_by('-views')


def robots(request):
    site_url = site_full_url()
    return render(request, 'robots.txt', context={'site_url': site_url}, content_type='text/plain')


class ArticleAddView(CreateView):
    model = Article
    template_name = 'blog/editor.html'
    fields = '__all__'

    # def get_context_data(self, **kwargs):
    #     return super().get_context_data(self, **kwargs)
    def post(self, request):
        post_dic = request.POST.copy()

        post_dic['author'] = 1 if request.user.id == None else request.user.id
        post_dic['summary'] = post_dic['body'][:60]
        post_dic['views'] = 0
        post_dic['slug'] = slugify(post_dic['title'])[:30]
        keywords = re.split(',|，| |。|，', post_dic['keywords'])
        post_dic.pop('keywords')
        if request.user.is_superuser:
            post_dic['reviewed'] = True
        form = ArticleEditForm(post_dic, request.FILES)

        # result = {}
        if not form.is_valid():
            return render(request, "blog/editor.html", {"form": form})

        # 如果 pk 不存在，为 None，那么 update_or_create 匹配失败，从而进入 create 流程
        # 否则 pk 存在表单中，那么尝试匹配数据库，如果命中，进行 update 操作，否则进行 create 操作
        article, created = Article.objects.update_or_create(title=form.cleaned_data['title'],
                                                            defaults=form.cleaned_data)
        for keyword in keywords:
            kw, created = Keyword.objects.get_or_create(name=keyword)
            article.keywords.add(kw)
            tag, created = Tag.objects.get_or_create(name=keyword, slug=slugify(keyword))
            article.keywords.add(kw)
            article.tags.add(tag)

        url = reverse('blog:detail', kwargs={'slug': article.slug})
        return HttpResponseRedirect(url)
