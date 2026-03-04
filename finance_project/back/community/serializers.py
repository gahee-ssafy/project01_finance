from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'author_username', 'author_nickname', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'author_username', 'author_nickname', 'created_at', 'updated_at']


class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author_username', 'author_nickname', 'created_at']
        read_only_fields = ['id', 'author_username', 'author_nickname', 'created_at']


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content',
            'author_username', 'author_nickname',
            'created_at', 'updated_at',
            'comments',
        ]
        read_only_fields = ['id', 'author_username', 'author_nickname', 'created_at', 'updated_at', 'comments']


# ✅ 게시글 작성/수정용 (POST/PUT/PATCH)
class PostWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.CharField(source="author.username", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "content", "author", "created_at")
