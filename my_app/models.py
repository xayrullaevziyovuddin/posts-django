from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django.template.defaultfilters import slugify
from markdownx.models import MarkdownxField


# Определение модели Category, представляющей категорию поста в блоге
class Category(models.Model):
    # Поле name хранит название категории, например, "Технологии" или "Наука"
    name = models.CharField(max_length=100)

    # Поле slug используется для создания удобных URL, связанных с категорией
    slug = models.SlugField(max_length=100, unique=False, blank=True, null=True)

    # Метод __str__ возвращает строковое представление категории (название категории)
    def __str__(self):
        return self.name

    # Метод save переопределен, чтобы автоматически генерировать slug на основе имени категории
    def save(self, *args, **kwargs):
        if not self.slug:  # Проверка, был ли slug уже установлен
            original_slug = slugify(self.name)  # Генерация slug из названия категории
            slug = original_slug
            count = 1
            # Цикл для создания уникального slug, если такой slug уже существует
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{count}"
                count += 1
            self.slug = slug  # Присвоение уникального slug
        super().save(*args, **kwargs)  # Вызов стандартного метода save


# Определение модели Post, представляющей пост в блоге
class Post(models.Model):
    # Внутренний класс, определяющий возможные статусы поста (черновик или опубликован)
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    # Поле title хранит заголовок поста
    title = models.CharField(max_length=255)

    # Поле body хранит текст поста, используя MarkdownxField для поддержки разметки Markdown
    body = MarkdownxField()

    # Поле date автоматически устанавливает текущую дату и время при создании поста
    date = models.DateTimeField(auto_now_add=True)

    # Поле user связано с моделью User, представляющей автора поста
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts', default=1
    )

    # Поле category связано с моделью Category (многие ко многим), пост может иметь несколько категорий
    category = models.ManyToManyField(
        Category, related_name='posts', blank=True
    )

    # Поле tags предоставляет возможность добавлять теги к постам с помощью библиотеки taggit
    tags = TaggableManager()

    # Поле image хранит изображение, связанное с постом, или оставляется пустым
    image = models.ImageField(upload_to='media/images', blank=True, null=True)

    # Поле status определяет текущий статус поста (черновик или опубликован)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)

    # Мета-класс для изменения порядка сортировки постов (по дате, от новых к старым)
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date'])  # Создание индекса по полю date для ускорения поиска
        ]

    # Метод __str__ возвращает строковое представление поста (заголовок поста)
    def __str__(self):
        return self.title

    # Метод get_absolute_url возвращает URL для просмотра деталей поста
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})


# Определение модели Image, представляющей изображения, связанные с постами
class Image(models.Model):
    # Поле post связывает изображение с конкретным постом
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')

    # Поле image хранит файл изображения, загружаемый в папку images/
    image = models.ImageField(upload_to='images/')

    # Поле uploaded_at автоматически устанавливает текущую дату и время при загрузке изображения
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Метод __str__ возвращает строковое представление изображения, включая заголовок связанного поста
    def __str__(self):
        return f"Image for post: {self.post.title}"


# Определение модели Comment, представляющей комментарии, связанные с постами
class Comment(models.Model):
    # Поле post связывает комментарий с конкретным постом
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    # Поле user связывает комментарий с автором (пользователем)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Поле text хранит текст комментария
    text = models.TextField()

    # Поле email хранит email автора комментария
    email = models.EmailField(default='default@example.com')

    # Поле created_at автоматически устанавливает текущую дату и время при создании комментария
    created_at = models.DateTimeField(auto_now_add=True)

    # Метод __str__ возвращает строковое представление комментария, включая имя автора и заголовок поста
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
