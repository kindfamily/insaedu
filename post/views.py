import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Comment, Post, Like, Tag
from .forms import CommentForm, PostForm

# post의 전체 리스트를 보여주는 뷰
def post_list(request, tag=None):
    # annotate
    # https://docs.djangoproject.com/en/1.9/ref/models/querysets/#annotate
    # 모든 태그의 내용을 검색하는데 annotate 함수를 이용해서 기준을 묶어낸다
    # num_post: post의 전체 숫자를 확인하고
    # order_by: - 옵션을 넣어서 내림차순으로 정렬 한후 tag_all에 저장한다

    tag_all = Tag.objects.annotate(num_post=Count('post')).order_by('-num_post')

    # tag가 있다면 filter()함수를 이용해서 조건에 맞게 여러행을 출력 타입은 QuerySet이다
    # https://wayhome25.github.io/django/2017/06/20/selected_related_prefetch_related/

    if tag:
        # prefetch_related: Returns a QuerySet that will automatically retrieve, in a single batch, related objects for each of the specified lookups.
        # select_related: Returns a QuerySet that will “follow” foreign-key relationships, selecting additional related-object data when it executes its query. This is a performance booster which results in a single more complex query but means later use of foreign-key relationships won’t require database queries.
        post_list = Post.objects.filter(tag_set__name__iexact=tag) \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')
    # tag가 없다면
    else:
        """
        
            sql 처리 속도 개선을 위한 코드
            .prefetch_related: ForeignKey, OneToOneField 관계에서 활용
            ForeignKey/OneToOneField 관계에서 Lazy하게 쿼리하지 않고, DB단에서 INNER JOIN 으로 쿼리할 수 있다.
            
            .select_related: ManyToManyField, ForeignKey의 reverse relation 에서 활용
            각 관계 별로 DB 쿼리를 수행하고, 파이썬 단에서 조인을 수행한다.
            https://wayhome25.github.io/django/2017/06/20/selected_related_prefetch_related/
            
        """
        post_list = Post.objects.all() \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user', ) \
            .select_related('author__profile', )

    # 댓글 폼(CommentForm) 을 forms.py 에서 comment_form에 집어넣는다
    comment_form = CommentForm()

    # paginator 패키지를 이용해서 post 리스트를 3개씩 보여준다
    paginator = Paginator(post_list, 3)
    page_num = request.POST.get('page') # 현재 페이지넘버 가져옴

    # paginator를 활용해서 페이지 보여주는 코드
    # https://cjh5414.github.io/django-pagination-%EC%82%AC%EC%9A%A9%EB%AA%A8%EB%93%88%EA%B2%B0%EC%A0%95/
    try:
        posts = paginator.page(page_num)            # 현재 페이지 넘버 가져와서 posts 변수에 담기
    except PageNotAnInteger:
        posts = paginator.page(1)                   # 페이지가 첫페이지만 있다면 1번 페이지 보여주기
    except EmptyPage:                               # 아무것도 없다면
        posts = paginator.page(paginator.num_pages) #

    if request.is_ajax():  # Ajax request 여부 확인
        return render(request, 'post/post_list_ajax.html', {
            'posts': posts,
            'comment_form': comment_form,
        })


    if request.method == 'POST':
        # request.POST 는 키로 전송된 자료에 접근할 수 있도록 해주는 사전과 같은 객체
        # get(): Key로 Value얻기(get)함수 post로 받은값을 'tag'을 key로 해서 값을 읽어냄
        tag = request.POST.get('tag')
        tag_clean = ''.join(e for e in tag if e.isalnum())
        # 특수문자 삭제 isalnum 문자와 숫자의 문자열을 탐지하는 파이썬 isalnum () 방법입니다.
        # 반환값이이 적어도 하나의 문자열이고 경우 모든 문자는 문자 또는 숫자 참, 그렇지 않으면 False를 반환

        return redirect('post:post_search', tag_clean)

    return render(request, 'post/post_list.html', {
        'tag': tag,
        'posts': posts,
        'comment_form': comment_form,
        'tag_all': tag_all,
    })


def my_post_list(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    user_profile = user.profile

    target_user = get_user_model().objects.filter(id=user.id).select_related('profile') \
        .prefetch_related('profile__follower_user__from_user', 'profile__follow_user__to_user')

    post_list = user.post_set.all()

    return render(request, 'post/my_post_list.html', {
        'user_profile': user_profile,
        'target_user': target_user,
        'post_list': post_list,
        'username': username,
    })


def my_post_list_detail(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    user_profile = user.profile

    target_user = get_user_model().objects.filter(id=user.id).select_related('profile') \
        .prefetch_related('profile__follower_user__from_user', 'profile__follow_user__to_user')

    post_list = Post.objects.filter(author=user) \
        .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                          'author__profile__follower_user', 'author__profile__follower_user__from_user', ) \
        .select_related('author__profile', )

    comment_form = CommentForm()

    paginator = Paginator(post_list, 3)
    page_num = request.POST.get('page')

    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.is_ajax():  # Ajax request 여부 확인
        return render(request, 'post/post_list_ajax.html', {
            'posts': posts,
            'comment_form': comment_form,
        })

    return render(request, 'post/my_post_list_detail.html', {
        'user_profile': user_profile,
        'username': username,
        'posts': posts,
        'comment_form': comment_form,
        'target_user': target_user,
    })


def follow_list(request, username):
    pass


@login_required
def follow_post_list(request):
    follow_set = request.user.profile.get_following
    post_list = Post.objects.filter(author__profile__in=follow_set) \
        .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                          'author__profile__follower_user', 'author__profile__follower_user__from_user', ) \
        .select_related('author__profile', )

    comment_form = CommentForm()

    paginator = Paginator(post_list, 3)
    page_num = request.POST.get('page')

    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.is_ajax():  # Ajax request 여부 확인
        return render(request, 'post/post_list_ajax.html', {
            'posts': posts,
            'comment_form': comment_form,
        })

    return render(request, 'post/post_list.html', {
        'follow_set': follow_set,
        'posts': posts,
        'comment_form': comment_form,
    })


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post.tag_save()
            messages.info(request, '새 글이 등록되었습니다.')
            return redirect('post:post_list')

    else:
        form = PostForm()
    return render(request, 'post/post_new.html', {
        'form': form,
    })


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.warning(request, '잘못된 접근입니다.')
        return redirect('post:post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            post.tag_set.clear()  # NOTE: ManyToManyField 의 모든 항목 삭제 (해당 인스턴스 내에서만 적용)
            post.tag_save()
            messages.success(request, '수정완료')
            return redirect('post:post_list')

    else:
        form = PostForm(instance=post)
    return render(request, 'post/post_edit.html', {
        'post': post,
        'form': form,
    })


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user or request.method == 'GET':
        messages.warning(request, '잘못된 접근입니다.')
        return redirect('post:post_list')

    if request.method == 'POST':
        post.delete()
        messages.success(request, '삭제완료')
        return redirect('post:post_list')


@login_required
@require_POST  # 해당 뷰는 POST method 만 받는다.
def post_like(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_like, post_like_created = post.like_set.get_or_create(user=request.user)

    if not post_like_created:
        post_like.delete()
        message = "좋아요 취소"
    else:
        message = "좋아요"

    context = {'like_count': post.like_count,
               'message': message,
               'nickname': request.user.profile.nickname}

    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required
def comment_new(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return render(request, 'post/comment_new_ajax.html', {
                'comment': comment,
            })
    return redirect("post:post_list")


@login_required
def comment_delete(request):
    pk = request.POST.get('pk')
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST' and request.user == comment.author:
        comment.delete()
        message = '삭제완료'
        status = 1

    else:
        message = '잘못된 접근입니다.'
        status = 0

    return HttpResponse(json.dumps({'message': message, 'status': status, }), content_type="application/json")


def comment_more(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        comments = post.comment_set.all()[4:]
        return render(request, 'post/comment_more_ajax.html', {
            'comments': comments,
        })
    return redirect("post:post_list")

