from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# Create your tests here.
class TestView(TestCase):
    # 하나의 TestCase 내에서 테스트 전 기본 설정 작업
    def setUp(self):
        self.client = Client()  # Client()를 사용하겠다.

        self.user_james = User.objects.create_user(username='James', password='somepassword')
        self.user_james.is_staff = True   # James에게 staff 권한 부여
        self.user_james.save()
        self.user_trump = User.objects.create_user(username='Trump', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_culture = Category.objects.create(name='culture', slug='culture')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        # 포스트(게시물)이 3개 존재하는 경우 (생성하기)
        self.post_001 = Post.objects.create(
            title="첫 번째 포스트입니다.",
            content="Hello World. We are the world.",
            author=self.user_james,
            category=self.category_programming,
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title="두 번째 포스트입니다.",
            content="1등이 전부가 아니잖아요.",
            author=self.user_trump,
            category=self.category_culture,
        )
        self.post_003 = Post.objects.create(    # 카테고리 없는 post
            title="세 번째 포스트입니다.",
            content="세 번째 포스트입니다.",
            author=self.user_trump,
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

    # 내비게이션 바 점검
    def navbar_test(self, soup):
        # 밑의 2개의 함수의 공통 부분
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 내비게이션 바 버튼의 href 링크가 올바른지 점검
        logo = navbar.find('a', text="Internet Programming")
        self.assertEqual(logo.attrs['href'], '/')

        home = navbar.find('a', text="Home")
        self.assertEqual(home.attrs['href'], '/')

        blog = navbar.find('a', text="Blog")
        self.assertEqual(blog.attrs['href'], '/blog/')

        about = navbar.find('a', text="About Me")
        self.assertEqual(about.attrs['href'], '/about_me/')

    def category_test(self, soup):
        category = soup.find('div', id='categories-card')

        self.assertIn('Categories', category.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', category.text)
        self.assertIn(f'{self.category_culture.name} ({self.category_culture.post_set.count()})', category.text)
        self.assertIn(f'미분류 (1)', category.text)

    def test_category_page(self):
        # 카테고리 페이지를 url로 불러오기
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        # soup를 검사하여 navbar, category 테스트
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리 name(badge 안 text)을 포함하고 있는가
        self.assertIn(self.category_programming.name, soup.h1.text)
        # 카테고리에 포함된 post만 포함하고 있는가
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        # 카테고리 페이지를 url로 불러오기
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        # soup를 검사하여 navbar, category 테스트
        self.navbar_test(soup)
        self.category_test(soup)
        # tag 이름을 h1 태그에 포함하고 있는가
        self.assertIn(self.tag_hello.name, soup.h1.text)
        # tag 이름과 post 1 title만 메인영역에 포함하고 있는가
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 로그인 하지 않으면 포스트 작성 접근 금지
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # 로그인 한다. 일반 사용자인 Trump는 작성 페이지 접근 X
        self.client.login(username='Trump',password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # 로그인 한다. 스태프인 James는 작성 페이지 접근 O
        self.client.login(username='James', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Create Post - Blog')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)  # Null이 아닌가? = input 태그가 존재하는가?

        # 블로그 포스트 작성하고 <submit> 버튼을 클릭했을 때
        self.client.post('/blog/create_post/',
                         {
                             'title': 'Post form 만들기',
                             'content': "Post form 페이지 만들기",
                             'tags_str': 'new tag; 한글 태그, python'
                         })
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post form 만들기")
        self.assertEqual(last_post.author.username, 'James')

        self.assertEqual(last_post.tags.count(), 3)  # 새로 생성한 포스트의 태그는 3개인가
        self.assertTrue(Tag.objects.get(name='new tag'))  # 이 태그가 새로 생성되어 존재하는가
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5) # 데이터베이스에 저장된 tag 모델 객체가 총 5개인가

    def test_update_post(self):
        update_url = f'/blog/update_post/{ self.post_003.pk }/'  # 포스트 수정 페이지 url
        # 로그인 하지 않은 경우
        response = self.client.get(update_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인 했지만 작성자(Trump)가 아닌 경우: James
        self.assertNotEqual(self.post_003.author, self.user_james)  # 작성자가 아닌 다른 사람인지 확인
        self.client.login(username='James', password='somepassword')  # username= self.user_james.username
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 403)  # 403: forbidden (접근 권한 금지)

        # 작성자가 로그인해서 접근하는 경우: Trump
        self.client.login(username='Trump', password='somepassword')  # username= self.post_003.author.username
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)  # 정상 접근

        # 수정 페이지가 잘 나타나는가
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, "Edit Post - Blog")
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)  # Null이 아닌가? = input 태그가 존재하는가?
        # 기존의 태그가 input의 value 속성에 저장되었는가
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        # 실제 수정 후 확인 - 수정한 내용을 잘 반영(저장)하는가
        response = self.client.post(update_url,
                         {
                            'title': '세 번째 포스트 수정',
                             'content': "안녕? 우리는 하나/... 반가워요",
                            'category': self.category_culture.pk,   # category는 외래키(다대일 관계)
                             'tags_str': '파이썬 공부; 한글 태그, some tag'
                         }, follow=True)  # update_url을 따라간다

        soup = BeautifulSoup(response.content, 'html.parser')   # 수정한 내용을 다시 파싱해서 받아오기
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트 수정', main_area.text)
        self.assertIn('안녕? 우리는 하나/... 반가워요', main_area.text)
        self.assertIn(self.category_culture.name, main_area.text)  # 특정 pk에 해당하는 category 이름 출력 확인

        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)


    def test_post_list(self):
        # 3개가 생성되었냐
        self.assertEqual(Post.objects.count(), 3)
        # 포스트 목록 페이지를 가져온다.
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드된다
        self.assertEqual(response.status_code, 200)
        # HTML요소에 쉽게 접근하기 위해 BeautifulSoup로 읽어들이고,
        # 'html.parser'로 요소 분석하여 파싱한 결과를 soup에 담는다.
        soup = BeautifulSoup(response.content, 'html.parser')
        # 페이지 타이틀은 'Blog'인가
        self.assertEqual(soup.title.text, 'Blog')
        # 내비게이션 바가 있다
        navbar = soup.nav
        # 내비게이션 바에 Blog, About Me 라는 문구가 있다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 내비게이션 바, 카테고리 카드 테스트 - 위의 함수 호출
        self.navbar_test(soup)
        self.category_test(soup)

        # 포스트(게시물)의 타이틀 3개가 메인영역에 나타나는가
        main_area = soup.find('div', id='main-area')
        # '아직 게시물이 없습니다' 안내문구가 더 이상 나타나지 않는가
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # setUp()에서 생성한 post_001,2,3의 필드가 목록 페이지 main 영역의 post_001,2,3_card에 나타나는가
        # setUp()에서 생성한 post의 tag도 post card 안에 있는가
        post_001_card= main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        # 메인 영역에서 작성자명으로 james, trump가 나타나는가
        self.assertIn(self.user_james.username.upper(), main_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)

        # 포스트(게시물)가 하나도 없는 경우
        Post.objects.all().delete()  #setUp()에서 미리 생성한 게 있으니까 먼저 다 삭제하기
        self.assertEqual(Post.objects.count(), 0)  # post 개수가 0개인가
        # 다시 페이지 새로고침
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 메인영역에 적절한 안내 문구가 포함되어 있는가
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)


    def test_post_detail(self):
        # 이 포스트의 url이 /blog/1인가
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 포스트 목록과 같은 내비게이션 바가 있는가
        # 내비게이션 바 & 카테고리 카드 테스트 - 위의 함수 호출
        self.navbar_test(soup)
        self.category_test(soup)

        # 포스트의 title은 웹 브라우저의 title에 있는가
        self.assertIn(self.post_001.title, soup.title.text)

        # 포스트의 title, category가 포스트 영역(post_area)에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.post_001.category.name, post_area.text)
        # 포스트의 tag가 post_area에 있는가
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        # 포스트의 내용이 post_area에 있는가
        self.assertIn(self.post_001.content, post_area.text)
        # 작성자 JAMES가 post_area에 있는가
        self.assertIn(self.user_james.username.upper(), post_area.text)