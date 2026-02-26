from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()



@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def login_view(request):

   
    if request.method == 'GET':
        return Response({
            "message": "Login API working. Please use POST method."
        })

   
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=400
            )

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
        
      
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):

    if request.method == 'GET':
        return Response({
            "message": "Login API working. Please use POST method."
        })

    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=400
            )

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "message": "Login successful",
            "access": str(access),
            "refresh": str(refresh),
            "access_expiry": datetime.fromtimestamp(access["exp"]),
            "refresh_expiry": datetime.fromtimestamp(refresh["exp"]),
        })