"""
Serializers pour l'app validation
"""

from rest_framework import serializers


class CodeSubmissionSerializer(serializers.Serializer):
    """Serializer pour la soumission de code"""

    code = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Code soumis par l'utilisateur"
    )

    def validate_code(self, value):
        """Valide que le code n'est pas vide"""
        if not value.strip():
            raise serializers.ValidationError("Le code ne peut pas être vide")
        return value


class TestResultSerializer(serializers.Serializer):
    """Serializer pour un résultat de test"""

    name = serializers.CharField()
    passed = serializers.BooleanField()
    points = serializers.IntegerField()
    message = serializers.CharField()


class ValidationResultSerializer(serializers.Serializer):
    """Serializer pour le résultat de validation"""

    success = serializers.BooleanField()
    results = TestResultSerializer(many=True)
    total_points = serializers.IntegerField()
    max_points = serializers.IntegerField()
    error = serializers.CharField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)
