from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostWriteSerializer,   # ✅ 추가 (아래 serializers.py에 만들어야 함)
    CommentSerializer
)
from .permissions import IsOwnerOrReadOnly


# 게시글 목록/작성
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        # ✅ 목록(GET)은 가볍게, 작성(POST)은 title/content 저장 가능하게
        if self.request.method == 'POST':
            return PostWriteSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# 게시글 상세/수정/삭제
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        # ✅ 상세(GET)은 댓글 포함 상세 serializer
        # ✅ 수정(PUT/PATCH)은 write serializer로 title/content 제대로 수정
        if self.request.method == 'GET':
            return PostDetailSerializer
        return PostWriteSerializer

    # ❌ author를 업데이트 때 덮어쓸 필요 없음 (작성자가 바뀌면 안 됨)
    # def perform_update(self, serializer):
    #     serializer.save(author=self.request.user)


# 특정 게시글의 댓글 리스트/작성
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id).order_by('created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        serializer.save(author=self.request.user, post_id=post_id)


# 댓글 수정/삭제
class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # ❌ 댓글도 작성자가 바뀌면 안 됨
    # def perform_update(self, serializer):
    #     serializer.save(author=self.request.user)
