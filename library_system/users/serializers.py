from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "password", "latitude", "longitude"
        ]


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "location"
        ]


class LoginSerializer(TokenObtainPairSerializer):
    ...


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, allow_null=False)


class PasswordRestSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False)

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if not user:
            raise ValidationError("The email is not Found")
        return value


class PasswordRestConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, max_length=25)
    re_new_password = serializers.CharField(min_length=8, max_length=25)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        re_new_password = attrs.get("re_new_password")
        uid = attrs.get("uid")
        token = attrs.get("token")
        if new_password != re_new_password:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Invalid UID.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token.")

        attrs['user'] = user
        return attrs
