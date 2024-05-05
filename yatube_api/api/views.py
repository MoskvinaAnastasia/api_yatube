from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from posts.models import Group, Post, Comment
from api.serializers import GroupSerializer, PostSerializer, CommentSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления группами.
    Создание, получение, обновление и удаление групп.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request):
        """
        Создает новую группу.
        Если данные действительны, создает новую группу и возвращает данные.
        группы с кодом статуса 201. Если нет, возвращает код статуса 405.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления постами.
    Создание, получение, обновление и удаление постов.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        """Создает новый пост."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Обновляет существующий пост."""
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Удаляет существующий пост."""
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super().perform_destroy(instance)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления комментариями.
    Создание, получение, обновление и удаление комментариев.
    """
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        """Создает новый комментарий."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        """Обновляет существующий комментарий."""
        instance = serializer.instance
        if instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого комментария запрещено!')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Удаляет существующий комментарий."""
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого комментария запрещено!')
        super().perform_destroy(instance)

    def get_queryset(self):
        """
        Возвращает запрос для получения всех комментариев к указанному посту.
        """
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return Comment.objects.filter(post=post)
