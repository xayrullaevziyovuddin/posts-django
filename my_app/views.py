# Импортируем необходимые модули и классы для работы с представлениями и формами.
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView
from config import settings  # Импортируем настройки проекта для использования в отправке электронной почты.
from .forms import LoginForm, SignupForm, CommentForm, SharePostForm  # Импортируем формы для регистрации, логина, комментариев и отправки поста.
from .models import Post, Image, Category  # Импортируем модели Постов, Изображений и Категорий.
from taggit.models import Tag  # Импортируем модель тегов.
from django.contrib import messages  # Импортируем модуль сообщений для вывода уведомлений пользователю.
from django.contrib.auth import authenticate, login, logout, views  # Импортируем функции аутентификации и управления сессиями пользователей.
from django.contrib.auth.models import User  # Импортируем модель пользователей.
from django.contrib.auth.mixins import LoginRequiredMixin  # Импортируем миксин для ограничения доступа к страницам только авторизованным пользователям.
from django.core.mail import send_mail  # Импортируем функцию для отправки электронной почты.

# Функция для отправки поста по электронной почте.
def share_post(request):
    # Проверяем, является ли запрос POST (отправка данных формы).
    if request.method == 'POST':
        form = SharePostForm(request.POST)  # Получаем данные из формы отправки поста.
        if form.is_valid():  # Проверяем, корректно ли заполнена форма.
            post_id = form.cleaned_data['post_id']  # Получаем ID поста из очищенных данных формы.
            recipient_email = form.cleaned_data['email']  # Получаем email получателя из очищенных данных формы.
            post = get_object_or_404(Post, id=post_id)  # Получаем пост по его ID или возвращаем ошибку 404, если он не найден.

            # Формируем тему и сообщение для отправки по электронной почте.
            subject = f"Пост: {post.title}"
            message = (
                f"Заголовок: {post.title}\n"
                f"Дата: {post.date}\n"
                f"Автор: {post.user}\n"
                f"Содержание:\n{post.body}\n\n"
                f"Изображение: {request.build_absolute_uri(post.images.all().first().image.url) if post.images.exists() else 'Изображение отсутствует'}"
            )

            # Отправляем письмо с постом на указанный email.
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

            # Выводим сообщение об успешной отправке.
            messages.success(request, "Пост был успешно отправлен по электронной почте.")
            return redirect('post_detail', pk=post_id)  # Перенаправляем пользователя на страницу подробностей поста.

    return redirect('index')  # Если запрос не POST, перенаправляем на главную страницу.

# Класс представления для отображения главной страницы блога с постами.
class IndexView(LoginRequiredMixin, ListView):
    model = Post  # Указываем модель, с которой будет работать это представление (Посты).
    template_name = 'blog-posts.html'  # Шаблон, который будет использоваться для отображения данных.
    context_object_name = 'posts'  # Имя контекста, которое будет передано в шаблон.
    paginate_by = 3  # Количество постов на одной странице.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Получаем контекст с данными по умолчанию.
        context['images'] = Image.objects.all()  # Добавляем в контекст все изображения.
        context['tags'] = Tag.objects.all()  # Добавляем в контекст все теги.
        context['categories'] = Category.objects.all()  # Добавляем в контекст все категории.

        context['latest_posts'] = Post.objects.order_by('-date')[:3]  # Добавляем в контекст три последних поста.

        return context  # Возвращаем обновленный контекст.

# Класс представления для отображения подробностей конкретного поста.
class PostDetailView(DetailView):
    model = Post  # Указываем модель, с которой будет работать это представление (Посты).
    template_name = 'blog-post-detail.html'  # Шаблон, который будет использоваться для отображения данных.
    context_object_name = 'post'  # Имя контекста, которое будет передано в шаблон.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Получаем контекст с данными по умолчанию.
        context['tags'] = Tag.objects.all()  # Добавляем в контекст все теги.
        context['categories'] = Category.objects.all()  # Добавляем в контекст все категории.
        context['images'] = Image.objects.all()  # Добавляем в контекст все изображения.
        context['latest_posts'] = Post.objects.order_by('-date')[:3]  # Добавляем в контекст три последних поста.
        context['comment_form'] = CommentForm()  # Добавляем в контекст форму для комментариев.
        context['comments'] = self.object.comments.all()  # Добавляем в контекст все комментарии к данному посту.
        return context  # Возвращаем обновленный контекст.

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Получаем объект поста.
        context = self.get_context_data(object=self.object)  # Получаем контекст с данным объектом.
        comment_form = CommentForm(request.POST)  # Получаем данные из формы комментария.

        if comment_form.is_valid():  # Проверяем, корректно ли заполнена форма.
            comment = comment_form.save(commit=False)  # Создаем объект комментария, но пока не сохраняем его в базе данных.
            comment.post = self.object  # Привязываем комментарий к текущему посту.
            comment.user = request.user  # Привязываем комментарий к текущему пользователю.
            comment.save()  # Сохраняем комментарий в базе данных.
            return redirect('post_detail', pk=self.object.pk)  # Перенаправляем на страницу подробностей поста.

        context['comment_form'] = comment_form  # Если форма невалидна, возвращаем форму с ошибками.
        return self.render_to_response(context)  # Отображаем страницу с данными и формой.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Инициализация объекта представления.

# Класс представления для отображения постов, которые имеют определенный тег.
class TaggedPostListView(ListView):
    model = Post  # Указываем модель, с которой будет работать это представление (Посты).
    template_name = 'blog-full.html'  # Шаблон, который будет использоваться для отображения данных.
    context_object_name = 'posts'  # Имя контекста, которое будет передано в шаблон.
    paginate_by = 3  # Количество постов на одной странице.

    def get_queryset(self):
        tag_slug = self.kwargs.get('slug')  # Получаем slug тега из параметров URL.
        return Post.objects.filter(tags__slug=tag_slug)  # Фильтруем посты по этому тегу.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Получаем контекст с данными по умолчанию.
        context['tags'] = Tag.objects.all()  # Добавляем в контекст все теги.
        context['categories'] = Category.objects.all()  # Добавляем в контекст все категории.
        return context  # Возвращаем обновленный контекст.

# Класс представления для отображения постов, которые относятся к определенной категории.
class CategoryPostListView(ListView):
    model = Post  # Указываем модель, с которой будет работать это представление (Посты).
    template_name = 'blog-full.html'  # Шаблон, который будет использоваться для отображения данных.
    context_object_name = 'posts'  # Имя контекста, которое будет передано в шаблон.
    paginate_by = 3  # Количество постов на одной странице.

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')  # Получаем slug категории из параметров URL.
        return Post.objects.filter(category__slug=category_slug)  # Фильтруем посты по этой категории.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Получаем контекст с данными по умолчанию.
        context['tags'] = Tag.objects.all()  # Добавляем в контекст все теги.
        context['categories'] = Category.objects.all()  # Добавляем в контекст все категории.
        return context  # Возвращаем обновленный контекст.

# Функция для регистрации нового пользователя.
def user_signup(request):
    if request.method == 'POST':  # Проверяем, является ли запрос POST (отправка данных формы).
        form = SignupForm(request.POST)  # Получаем данные из формы регистрации.
        if form.is_valid():  # Проверяем, корректно ли заполнена форма.
            form.save()  # Сохраняем нового пользователя в базе данных.
            messages.success(request,
                             'Your account has been created successfully!')  # Выводим сообщение об успешной регистрации.
            return redirect('login')  # Перенаправляем пользователя на страницу входа в систему.
        else:
            messages.error(request,
                           'Please correct the errors below.')  # Если форма невалидна, выводим сообщение об ошибке.
    else:
        form = SignupForm()  # Если запрос не POST, создаем пустую форму для регистрации.
    return render(request, 'accounts/signup.html', {'form': form})  # Отображаем страницу регистрации с формой.

    # Функция для входа пользователя в систему.
def user_login(request):
        if request.method == 'POST':  # Проверяем, является ли запрос POST (отправка данных формы).
            form = LoginForm(request.POST)  # Получаем данные из формы входа.
            if form.is_valid():  # Проверяем, корректно ли заполнена форма.
                username = form.cleaned_data['username']  # Получаем введенное имя пользователя или email.
                password = form.cleaned_data['password']  # Получаем введенный пароль.

                try:
                    user_exists = User.objects.get(username=username)  # Пытаемся найти пользователя по имени.
                except User.DoesNotExist:
                    user_exists = User.objects.filter(email=username).first()  # Если не найден, ищем по email.

                if user_exists:
                    user = authenticate(request, username=user_exists.username,
                                        password=password)  # Аутентифицируем пользователя.
                    if user:
                        login(request, user)  # Входим в систему, если аутентификация успешна.
                        return redirect('index')  # Перенаправляем на главную страницу.
                    else:
                        messages.error(request,
                                       'Неправильный пароль.')  # Если пароль неверный, выводим сообщение об ошибке.
                else:
                    messages.error(request,
                                   'Пользователь с таким именем или email не найден.')  # Если пользователь не найден, выводим сообщение.
            else:
                messages.error(request,
                               'Ошибка в заполнении формы.')  # Если форма невалидна, выводим сообщение об ошибке.

        else:
            form = LoginForm()  # Если запрос не POST, создаем пустую форму для входа.

        return render(request, 'accounts/login.html', {'form': form})  # Отображаем страницу входа с формой.


def user_logout(request):
    logout(request)  # Выходим из системы, завершив сессию пользователя.
    messages.success(request, 'Вы успешно вышли из системы.')  # Выводим сообщение об успешном выходе.
    return redirect('login')  # Перенаправляем на страницу входа.

