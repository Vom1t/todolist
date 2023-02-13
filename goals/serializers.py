from django.db import transaction
from rest_framework import serializers, exceptions
from rest_framework.exceptions import PermissionDenied

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import GoalCategory, GoalComment, Goal, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания категории"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')

    def validate_board(self, value: Board) -> Board:
        """Функция проверки на разрешение редактирования доски, и не удалена ли она"""
        if value.is_deleted:
            raise serializers.ValidationError('Board is deleted')

        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории целей"""

    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'board')
        extra_kwargs = {
            'is_deleted': {'write_only': True}
        }


class GoalCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания целей"""

    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory):
        """
        Функция валидации данных категории целей. Проверяет, является ли
        пользователь создателем категории, или является writer'ом
        """

        if not BoardParticipant.objects.filter(
                board_id=value.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


class GoalSerializer(serializers.ModelSerializer):
    """Сериализатор цели"""

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory):
        """
        Функция валидации данных категории целей.
        Проверяет, является ли пользователь создателем категории целей
        """

        if self.context['request'].user.id != value.user_id:
            raise exceptions.PermissionDenied
        return value


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания комментария"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, value: Goal):
        """
        Функция валидации данных комментарий целей.
        Проверяет, является ли пользователь создателем категории целей или writer'ом
        """

        if not BoardParticipant.objects.filter(
                board=value.category.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев"""

    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')


class BoardCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания новой доски"""

    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Сериализатор других участников доски"""

    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    """Сериализатор отображения доски"""

    participants = BoardParticipantSerializer(many=True)

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance, validated_data):
        """Функция редактирования и добавления участников доски"""

        owner = self.context['request'].user
        new_participants = validated_data.pop('participants', [])
        new_by_id = {part['user'].id: part for part in new_participants}

        old_participants = instance.participants.exclude(user=owner)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()
                else:
                    if old_participant.role != new_by_id[old_participant.user_id]['role']:
                        old_participant.role = new_by_id[old_participant.user_id]['role']
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    board=instance, user=new_part['user'], role=new_part['role']
                )

            if title := validated_data.get('title'):
                instance.title = title
                instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Сериализатор списка досок"""
    class Meta:
        model = Board
        fields = '__all__'
