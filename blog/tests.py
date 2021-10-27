from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.
class TestView(TestCase):
    # 하나의 TestCase 내에서 테스트 전 기본 설정 작업
    def setUp(self):
        self.client = Client()  # Client()를 사용하겠다.

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

    def test_post_list(self):
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

        # 내비게이션 바 테스트 - 위의 함수 호출
        self.navbar_test(soup)

        # 포스트(게시물)가 하나도 없는 경우
        self.assertEqual(Post.objects.count(), 0)
        # 메인영역에 적절한 안내 문구가 포함되어 있는가
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # 포스트(게시물)이 2개 존재하는 경우 (생성하기)
        post_001 = Post.objects.create(
            title="첫 번째 포스트입니다.",
            content="Hello World. We are the world."
        )
        post_002 = Post.objects.create(
            title="두 번째 포스트입니다.",
            content="1등이 전부가 아니잖아요."
        )
        # 2개가 생성되었냐
        self.assertEqual(Post.objects.count(), 2)

        # 목록페이지를 새롭게 불러와서(새로고침)
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 포스트(게시물)의 타이틀 2개가 메인영역에 나타나는가
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # '아직 게시물이 없습니다' 안내문구가 더 이상 나타나지 않는가
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)


    def test_post_detail(self):
        # 포스트 하나 생성
        post_001 = Post.objects.create(
            title="첫 번째 포스트입니다.",
            content="Hello World. We are the world."
        )
        # 이 포스트의 url이 /blog/1인가
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 포스트 목록과 같은 내비게이션 바가 있는가
        # 내비게이션 바 테스트 - 위의 함수 호출
        self.navbar_test(soup)

        # 포스트의 title은 웹 브라우저의 title에 있는가
        self.assertIn(post_001.title, soup.title.text)

        # 포스트의 title은 포스트 영역(post_area)에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)

        # 포스트 작성자가 있는가
        # 아직 작성 중

        # 포스트의 내용이 post_area에 있는가
        self.assertIn(post_001.content, post_area.text)