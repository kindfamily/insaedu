########
# info #
########


"""

>> 모듈 불러오는 방법 3가지
import 모듈
→ 해당 모듈 전체를 가져온다.
    사용하려면 항상 '모듈명.메소드' 와 같이 모듈명을 앞에 붙여주어야 한다.

from 모듈 import 메소드 / 변수
→ 해당 모듈 내에 있는 특정 메소드나 모듈 내 정의된 변수를 가져온다.
    가져온 메소드나 변수를 앞에 모듈명을 붙이지 않고 그대로 사용할 수 있다.
    다만, 이름이 같은 변수나 메소드가 존재할 경우 대체된다.

from 모듈 import * 이라고 하면 import 모듈과 동일하다. (사용 시 모듈명 붙이는 것 빼고)


>> 파이썬에서의 _ 언더스코어
https://mingrammer.com/underscore-in-python/
https://gomguard.tistory.com/125
파이썬에선 (_) 를 사용하는 경우들이 있습니다.
1. 인터프리터에서 마지막 값을 저장하고 싶을 때
2. 값을 무시하고 싶을 때
3. 변수나 함수명에 특별한 의미를 부여하고 싶을 때
4. 숫자 리터럴 값의 자릿수 구분을 위한 구분자로써 사용할 때


>> () [] {}
[] array : 배열을 선언 초기화 할때
arr = [] # 빈 배열을 만들 때 []사용
arr = [1,2,3,4] #원소가 있는 배열을 만들 때 []사용

arr[3] #배열의 3번째 원소에 접근할 때 []사용


() tuple : 튜플을 선언&초기화 할때
mytuple = () #빈 튜플 생성할 때 ()사용
mytuple = (1,2,3,4) # 원소가 있는 튜플을 만들 때 ()사용

mytuple[3] # 튜플의 원소에 접근할 때 []사용

{} dictionary : 딕셔너리를 선언&초기화할 때mydictionary = {} #빈 딕셔너리 생성 시 {}사용
mydictionary = {"mouse":3, "penguin":5}

mydictionary["mouse"] # key("mouse")에 대응하는 value(3)에 접근할 때 사용
mydictionary["cat"] = 1 # key("cat")에 대한 value(1) 생성

>> django 에서 문자형 사용할때
django 모델형에선 문자형을 CharField 와 TextField 라는 걸로 나타낼 수 있다.
차이점은 CharField 는 256 글자(혹은 byte) 이하에서만 쓸 수 있고,
TextField 는 그보다 훨씬 많은(긴) 글자를 써넣을 수 있다는 점이다. \

"""

###########
# package #
###########

"""

    name          : imagekit
    about         : 이미지 처리를 위한 패키지
    moduleName    : imagekit.models, imagekit.processors
    method        : ProcessedImageField, ResizeToFill
    document      : https://pypi.org/project/django-imagekit/
    function      : 업로드 위치지정, 사이즈변경(150x150), 해상도조정
    more function : Watermark
    option        : blank=True(빈칸으로 업로드 가능)
    
    from django.conf import settings    
    https://docs.djangoproject.com/en/2.2/ref/contrib/auth/

    import re # 정규 표현식을 지원하기 위한 re(regular expression) 모듈
"""

from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import re


"""
    name    : photo_path
    파라미터  : instance( photo 모델 ), filename( 업로드된 파일명 )
    module  : random ( 설명글: https://wikidocs.net/79 )
    method  : choice(안에 있는 원소를 아무거나 하나 뽐아줌)
    method2 : string 메소드, string.ascii_letters 
               -> ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz)
    method3 : string.ascii.letters : 대소문자 상관없이 랜덤한 문자를 생성한다 
                , string.ascii_lowercase : 소문자만 생성, string.ascii_lowercase : 대문자만 생성
    내장함수  : range > range(1,3)은 1,2,3과 같다, range(8)은 0,1,2,3,4,5,6,7,8,  
    내장함수2 : join( 리스트를 구분자를 포함해 문자열로 변환 ) ''.join(arr)은 ''가 구분자로 하나씩합해서 8자리 단어를만듬 arr은 리스트
    내장함수3 : split('.')[-1] . 문자를 단위로 잘라서 배열로 만들고 마지막 요소를 추출한다
    내장함수3 : accounts/{}/{}.{}'.format(instance.user.username, pid, extension) 
                통해 포매팅 가능 acounts뒤에 있는 {} 안에 format안에있는 3개의 인자를 하나씩 입력한다


    _ : 인덱스 무시 하는 파이썬 문법
    for _ in range(8)
    인덱싱이 필요없아 
    
    일반적인 for in 문
    var_list = [1, 3, 5, 7]
    for i in var_list:
         print(i)
    
    결과: 1,3,5,7
"""

def photo_path(instance, filename):
    from time import strftime
    from random import choice
    import string # string.ascii_letters : ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return '{}/{}/{}.{}'.format(strftime('post/%Y/%m/%d/'), instance.author.username, pid, extension)

"""
    # Post 클래스 객체는 django.db.models.Model 이라는 클래스의 서브클래스
    # Post 클래스 객체는 (models.Model) -> 항상 Model 클래스를 상속받는다
    # 모델 클래스의 어트리뷰트로 데이터베이스의 필드(컬럼)을 표현 한다
    # Be careful with related_name에서 정의한 쿼리인 related_name 은 유일해야한다 나중에 검색하기 위한 태그
    # on_delete=models.CASCADE : 모델 A 와 모델 B가 N:1 관계일 때, 모델A에 on_delete=models.CASADE 구문이 설정되어있으면, 모델 B의 어떤 레코드가 삭제되면 삭제될 모델 B의 레코드와 관련있는 모델 A의 레코드들도 연차적으로 삭제됩니다
    # 연관된 어떤 모델(Profile) 이 받은 행위에 같은 영향(행위)을 받게 한다는 것으로 생각하시면 됩니다.
    # settings.AUTH_USER_MODEL venv> lib> python3,7 > django> conf > global_setting.py 에서 AUTH_USER_MODEL = 'auth.User' 확인
    # settings.AUTH_USER_MODEL을 외래키로 지정 한다 settings.AUTH_USER_MODEL 은 djanog 의 global_setting.py 파일에 정의 되어 있다
    # upload_to: photo_path 사진의 저장할 위치를 지정
    # processors: 사이즈를 600 x 600 사이즈로 지정
    # format: JPEG 으로 변경
    # options > quality : 90% 품질로 변형해서 올린다
    # CharField : 제한된 문자열 필드 타입. 최대 길이를 max_length 옵션에 지정해야 한다. 문자열의 특별한 용도에 따라 CharField의 파생클래스로서, 이메일 주소를 체크를 하는 EmailField, IP 주소를 체크를 하는 GenericIPAddressField, 콤마로 정수를 분리한 CommaSeparatedIntegerField, 특정 폴더의 파일 패스를 표현하는 FilePathField, URL을 표현하는 URLField 등이 있다.
    # DateTimeField : 날짜와 시간을 갖는 필드. 날짜만 가질 경우는 DateField, 시간만 가질 경우는 TimeField를 사용한다.
    # auto_now vs auto_now_add : auto_now is set or both auto_now_add is set and the object is new
    # created_at 은 처음 만들어지는 것이기 때문에 auto_now_add 를 사용 , updated_at은 시간을 변경하는 것이기 때문에 auto_now를 사용
    # blank 값이 True이면, 필드값을 입력하지 않아도 됩니다. 기본값은 False 입니다
    # ManyToManyField : 다대다 관계 위치 인수가 요구된다, ForeignKey와 동일하게 작동한다
"""

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = ProcessedImageField(upload_to=photo_path,
                                processors=[ResizeToFill(600, 600)],
                                format='JPEG',
                                options={'quality': 90})
    content = models.CharField(max_length=140, help_text="최대 140자 입력 가능")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tag_set = models.ManyToManyField('Tag', blank=True)                 # 빈칸을 넣어도 되는 Tag모델을 가져와서 tag_set 변수에 담는다
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,    # auth.User 모듈과 many-to-many 관계의 모듈을 만든다
                                           blank=True,
                                           related_name='like_user_set',# 나중에 검색이 가능하도록 하는 이름을 like_user_set으로 지정
                                              through='Like')           # 중계해주는 모델을 Like로 지정한다

    class Meta:
        ordering = ['-created_at']

    # 여기여기 서 부터 보면됨
    # NOTE: content에서 tags를 추출하여, Tag 객체 가져오기, 신규 태그는 Tag instance 생성, 본인의 tag_set에 등록,
    # 객체 지향 프로그램에서 인스턴스는 class에 속하는 객체를 이야기 한다
    # https://wayhome25.github.io/django/2017/06/22/custom-template-filter/
    def tag_save(self):
        pattern = re.compile("r'#(\w+)\b'")  # 여러번 사용하는 패턴은 컨파일 해서 사용하는게 2배이상 더 빠르다
        tags = re.findall(pattern, self.content)
        # tags = re.findall(r'#(\w+)\b', self.content)
        # 정규표현식 번역기 https://regexper.com/
        # content 의 내용에서 정규표현식 규칙대로 찾아라

        # #: #이 있는
        # r' ' : raw string으로 백슬래시 문자를 해석하지 않고 남겨두기 r'가 없었다면 '#(\\w+)\\b' 로 입력해야함
        # \w+: 최소한 한개의 알파벳 또는 한개의 숫자[a-zA-Z_0-9]와 동일
        # ()안에 것을 찾아주세요
        # \b: 다음단어와의 경계


        if not tags:
            return

        for t in tags:
            tag, tag_created = Tag.objects.get_or_create(name=t)
            self.tag_set.add(tag)  # NOTE: ManyToManyField 에 인스턴스 추가

    @property
    def like_count(self):               # like 숫자를 카운트 하는 함수
        return self.like_user_set.count()

    def __str__(self):                  #
        return self.content

# tag
class Tag(models.Model):
    name = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.name

# 좋아요 클래스
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # user와 post의 유일무이한 관계를 mata클래스를 통해서 기록
    class Meta:
        unique_together = (
            ('user', 'post')
        )

#  댓글 클래스
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # admin 페이지에 정렬순서를 id값 역순으로 표시 새글이 위로 가도록 표시
    class Meta:
        ordering = ['-id']

    # [커스텀 요소] 전체 커맨트 불러오는 함수 인스턴스 만들어 보기
    # [커스텀 요소] 로그인하고 사용자 정보 불러와서 나한테 달린 댓글만 보이도록 만들어 보기
    # [커스텀 요소] 대댓글

    def __str__(self):
        return self.content
