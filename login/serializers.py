from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    
    def validate(self, data):
        email = data.get("email")
        phone = data.get("phone_number")
        role = data.get("role")

        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "Email already exists"
            })

        
        if phone and len(phone) < 10:
            raise serializers.ValidationError({
                "phone_number": "Phone number must be at least 10 digits"
            })

        
        if role == "ADMIN":
            raise serializers.ValidationError({
                "role": "You cannot create ADMIN user from API"
            })

        return data
