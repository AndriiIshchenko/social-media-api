from django.db import transaction
from django.forms import fields
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from posts.models import Like, Post


class LikeSerializer(serializers.ModelSerializer):
    like_type = serializers.ChoiceField(choices=Like.CHOICES)
    class Meta:
        model = Like
        fields = ("like_type",)




class PostSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ("id", "content", "user", "created_at", "updated_at", "likes_amount")


class PostDetailSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ("id", "user", "created_at", "updated_at", "content", "likes_amount")

    # def update(self, instance, validated_data):
    #     with transaction.atomic():
    #         like_data = validated_data.pop("likes")
    #         order = Order.objects.create(**validated_data)
    #         for ticket_data in tickets_data:
    #             Ticket.objects.create(order=order, **ticket_data)
    #         return order
    #     return super().update(instance, validated_data)