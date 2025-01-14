from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category


# Create your tests here.


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_korea = User.objects.create_user(username='Korea', password='somepassword')
        self.user_test = User.objects.create_user(username='Tester', password='somepassword')
        self.category_propramming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_propramming,
            author=self.user_korea
        )
        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부입니다.',
            category=self.category_music,
            author=self.user_test
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='카테고리가 없어요',
            author=self.user_test
        )

        def category_card_test(self, soup):
            categories_card = soup.find('div', id='categories-card')
            self.assertIn('Categories', categories_card.text)
            self.assertIn(f'{self.categroy_programming.name} ({self.categroy_programming.post_set.count()})', categories_card.text)
            self.assertIn(f'{self.categroy_music.name}({self.categroy_music.post_set.count()})', categories_card.text)
            self.assertIn(f'미분류 (1)', categories_card.text)

        def test_post_list(self):
            # 포스트가 있는 경우
            self.assertEqual(Post.objects.count(), 3)

            response = self.client.get('/blog/')
            self.assertEqual(response.status_code, 200)
            soup = BeautifulSoup(response.content, 'html.parser')

            self.navbar_test(soup)
            self.category_card_test(soup)

            main_area = soup.find('div', id='main-area')
            self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

            post_001_card = main_area.find('div', id='post-1')
            self.assertIn(self.post_001.title, post_001_card.text)
            self.assertIn(self.post_001.category.name, post_001_card.text)

            post_002_card = main_area.find('div', id='post-2')
            self.assertIn(self.post_002.title, post_002_card.text)
            self.assertIn(self.post_002.category.name, post_002_card.text)

            post_003_card = main_area.find('div', id='post-3')
            self.assertIn(self.post_003.title, post_003_card.text)
            self.assertIn(self.post_003.category.name, post_003_card.text)

            self.assertIn(self.user_korea.username.upper(), main_area.text)
            self.assertIn(self.user_test.username.upper(), main_area.text)

            # 포스트가 없는 경우
            Post.objects.all().delete()
            self.assertEqual(Post.objects.count(), 0)
            response = self.client.get('/blog/')
            soup = BeautifulSoup(response.content, 'html.parser')
            main_area = soup.find('div', id='main-area')
            self.assertIn('아직 게시물이 없습니다.', main_area.text)



    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='홈으로')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')




    def test_post_detail(self):
        # 1.1 포스트가 하나 있다.
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. we are the world.',
        )

        # 1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url은 접근하면 정상적으로 작동한다.(status code: 200).
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)
        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 있다.
        self.assertIn(post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        # 2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다(미완성)
        # 2.6 첫 번째 포스트의 내용이(content) 포스트 영역에 있다
        self.assertIn(post_001.content, post_area.text)

