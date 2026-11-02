from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from main.models import Message
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.serializers import MessageSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def message_list(request):
    if request.method in ("GET", "HEAD"):
        messages = Message.objects.prefetch_related(
            "starred_by"
        ).order_by("-created_at", "-pk")

        query = request.query_params.get("message", "").strip()
        if query:
            messages = messages.filter(message__icontains=query)

        serializer = MessageSerializer(
            messages, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = MessageSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def message_detail(request, message_id):
    message = get_object_or_404(
        Message.objects.prefetch_related("starred_by"), pk=message_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = MessageSerializer(message, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = MessageSerializer(
        message, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def message_star(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    if message.starred_by.filter(pk=request.user.pk).exists():
        message.starred_by.remove(request.user)
    else:
        message.starred_by.add(request.user)

    serializer = MessageSerializer(message, context={"request": request})
    return Response(serializer.data)
