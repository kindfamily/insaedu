import json
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import logout as django_logout
from .forms import SignupForm, ProfileForm, LoginForm
from .models import Profile, Relation

# from django.conf import settings
# from django.contrib.auth.views import LoginView
# from allauth.socialaccount.models import SocialApp
# from allauth.socialaccount.templatetags.socialaccount import get_providers

"""
    함수명: login_check
    기능1: 로그인 실패시 accounts/login_fail_info.html로 이동
    기능2: 로그인 성공시 / 로 이동
"""

def login_check(request):
    if request.method == "POST":
        LoginForm(request.POST)                                          # 사용자가 로그인 폼에 입력한 값
        name = request.POST.get('username')                             # 이름
        pwd = request.POST.get('password')                              # 비번

        user = authenticate(username=name, password=pwd)                # authentiacte 내장 함수를 이용해서 DB의 내용과 비교
        if user is not None:                                            # 로그인 성공시
            login(request, user)                                        # 로그인 시켜라
            return redirect("/")                                        # 로그인후 / 루트로 이동
        else:                                                           # 로그인 실패시
            return render(request, 'accounts/login_fail_info.html')     # login_fail_info.html로 이동
    else:                                                               # get 방식인 경우 로그인 안되 있을때 펄로우 버튼누르면 리다이렉트되서 로그인 페이지로 이동
        form = LoginForm()                                              # LoginForm을 forms.py에서 불러와서 form에 넣기
        return render(request, 'accounts/login.html', {"form":form})    # login.html로 이동 하면서 form형식을 함께 보내기


def logout(request):                                                    # logout 함수
    django_logout(request)                                              # django_logout 내장함수 이용해서 현재 유저 로그아웃
    return redirect("/")                                                # / 로 이동


def signup(request):
    if request.method == 'POST':                                        # POST 요청을 받으면
        form = SignupForm(request.POST, request.FILES)                  # forms.py 에서 만든 SignupForm에 받은 POST 값과 FILES를 form 변수에 담고
        if form.is_valid():                                             # 넘어온 값이 있다면
            form.save()                                                 # form.save()로 값을 저장하고
            return redirect('accounts:login')                           # accounts앱의 name= login url로 이동
    else:
        form = SignupForm()                                             # SignupForm을 form.py 파일에서 불러온다
    return render(request, 'accounts/signup.html', {                    # 요청을 받으면 signup.html 파일에 form 값을 전달해서 불러온다
        'form': form,
    })


@login_required                                                         # 로그인을 해야만 실행할수 있다는 데코레이터
def password_change(request):
    if request.method == 'POST':                                        # 만약 POST 방식으로 전달된 값이면 실행해라
        form = PasswordChangeForm(request.user, request.POST)           # django.contrib.auth.forms에 기본으로 있는 PasswordChangeForm을 불러와서 요청받은 user
        if form.is_valid():
            user = form.save()

            """
            
                # 장고의 로그인은 session 값을 가지고 하는데
                # update_session_auth_hash(request, user) //https://docs.djangoproject.com/en/2.2/topics/auth/default/
                # 를 통해 세션을 해제가능
                # Important!
            
            """
            update_session_auth_hash(request, user)
            messages.success(request, '비밀번호가 정상적으로 변경되었습니다.')  # 정상적으로 비밀번호가 변경되었다면 메시지 출력
            return redirect('post:my_post_list', request.user.username) # post 앱에 my_post_list 이름을 가진 곳으로 user의 username과 함께 이동한다

        else:
            messages.error(request, '오류가 발생하였습니다.')                # 오류가 있다면 오류 메시지 보냄
    else:
        form = PasswordChangeForm(request.user)                         # get 방식이라면 user 값을 form에 담는다
    return render(request, 'accounts/password_change.html', {           # form 값과 함께 password_change.html 파일로 이동
        'form': form,
    })


@login_required
def account_change(request):
    profile = get_object_or_404(Profile, pk=request.user.profile.id)        # get_object_or_404 : 함수는 Django 모델을 첫번째 인자로 받고, 몇개의 키워드 인수를 모델 관리자의 get() 함수에 넘깁니다. 만약 객체가 존재하지 않을 경우, Http404 예외가 발생합니다.
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)   # forms.py 에서 ProfileForm
        if form.is_valid():
            # 사용되지 않는 변수라면 아래와 같이 색깔이 비활성화됨 지워도 잘 작동
            profile = form.save()
            messages.success(request, '회원정보가 정상적으로 변경되었습니다.')       # 정보변경에 성공했다면 post 앱에 my_post_list url로 이동하면서 request.user.username을 함께 보낸다
            return redirect('post:my_post_list', request.user.username)
        else:
            messages.error(request, '오류가 발생하였습니다.')                     # 오류 메시지
    else:
        form = ProfileForm(instance=profile)                                # instance란?
    return render(request, 'accounts/account_change.html', {
        'form': form,
    })


@login_required
@require_POST   # POST를 제외한 다른 접근에 대해서는 빈 페이지와 405코드를 반환한다.# https://docs.djangoproject.com/en/1.10/topics/http/decorators/#allowed-http-methods
def follow(request):
    from_user = request.user.profile
    pk = request.POST.get('pk')
    """
    
        # get_object_or_404() 함수는 Django 모델을 첫번째 인자로 받고, 몇개의 키워드 인수를 모델 관리자의 get() 함수에 넘깁니다. 만약 객체가 존재하지 않을 경우, Http404 예외가 발생합니다.
        # pk값을 받아서 Profile 객체의 존재여부를 확인하고 to_user 변수에 담는다
        # Relations 모델을 가져와서 get_or_create 메소드를 이용해서 
        # created True 라면 인스턴트가 get_or_create 메서드에 의해 생성 되었다는 이야기
        # 만약 created 가 true라면 === 팔로우를 한다면
        # 상태를 1로 바꾸고
        # 아니라면 팔로우 취소라는 메시지를 보내고 관계를 삭제한다
        # get_or_create 는 일종에 스위치 https://whatisthenext.tistory.com/121
        # delete() 사용법 https://wayhome25.github.io/django/2017/04/01/django-ep9-crud/
        
    """
    to_user = get_object_or_404(Profile, pk=pk)
    relation, created = Relation.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        message = '팔로우 시작!'
        status = 1
    else:
        relation.delete()
        message = '팔로우 취소'
        status = 0

    context = {
        'message': message,
        'status': status,
    }
    # HttpRequest와 HttpResponse는?
    # HttpRequest : 요청에 대한 메타정보를 가지고 있는 객체
    # HttpResponse : 응답에 대한 메타정보를 가지고 있는 객체
    # context의 값을 json.dumps를 이용해 ajax  통신을 위해서 json 방식으로 보냄
    # content_type을 json 으로 해서 보냄
    return HttpResponse(json.dumps(context), content_type="application/json")