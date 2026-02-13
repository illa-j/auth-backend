from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import EmailVerificationToken, PasswordChangeToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data):
        validated_data.pop("is_active", None)
        return get_user_model().objects.create_user(**validated_data, is_active=False)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "username", "email", "is_staff")
        read_only_fields = (
            "id",
            "is_staff",
        )


class TokenBlacklistSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        try:
            self.token = RefreshToken(value)
        except Exception:
            raise serializers.ValidationError("Invalid refresh token")

    def save(self, **kwargs):
        if self.token:
            try:
                self.token.blacklist()
            except Exception:
                pass


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            token_obj = EmailVerificationToken.objects.get(token=value)
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")

        now = timezone.now()
        if token_obj.created_at < now - timezone.timedelta(days=1):
            raise serializers.ValidationError("Token has expired")


        self.token_obj = token_obj
        return value

    def save(self):
        user = self.token_obj.user
        user.is_active = True
        user.save(update_fields=["is_active"])
        self.token_obj.delete()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        validators=[validate_password],
    )


class ConfirmPasswordChangeSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            token_obj = PasswordChangeToken.objects.get(token=value)
        except PasswordChangeToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")

        if token_obj.is_expired():
            raise serializers.ValidationError("Token has expired")

        self.token_obj = token_obj
        return value

    def save(self):
        user = self.token_obj.user
        user.password = self.token_obj.password_hash
        user.save(update_fields=["password"])

        self.token_obj.delete()
        return user


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True, help_text="Authorization code from Google"
    )

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Authorization code is required")
        return value


class GoogleTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True, help_text="Google ID token from frontend"
    )

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required")
        return value


class GoogleAuthResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(help_text="JWT access token")
    refresh_token = serializers.CharField(help_text="JWT refresh token")
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj.get("user")
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
        }
