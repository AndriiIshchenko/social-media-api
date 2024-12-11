from tokenize import TokenError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            # Blacklist the token
            token.blacklist()
            return Response({"message": "Token successfully blacklisted"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
