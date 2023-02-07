import redis
from django.core.management.base import BaseCommand
from django.db.models import Q

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import GetUpdatesResponse, Message, MessageFrom
from goals.models import Goal, GoalCategory
from todolist.settings import BOT_TOKEN


redis_instance = redis.StrictRedis(host='redis')


class Command(BaseCommand):
    help = 'Run telegram-bot'

    def __init__(self):
        super().__init__()
        self.tg_client = TgClient(BOT_TOKEN)
        self.tg_user = TgUser
        self.allow_commands_list = {
            '/goals': self._get_goals,
            '/create': self._create_category,
        }
        self.commands = {
            b'/goals': self._get_goals,
            b'/create': self._create_category,
            b'set_name_category': self._set_name_category,
            b'set_name_goal': self._set_name_goal,
        }

    def _check_user_existence(self, user: MessageFrom, chat_id: str) -> TgUser:
        tg_user, _ = self.tg_user.objects.get_or_create(tg_id=chat_id,
                                                        username=user.id)
        return tg_user

    def handle(self, *args, **options):
        offset = 0

        while True:
            res: GetUpdatesResponse = self.tg_client.get_updates(offset=offset)
            if res:
                for item in res.result:
                    offset = item.update_id + 1
                    chat_id = item.message.chat.id
                    user = item.message.from_
                    tg_user: TgUser = self._check_user_existence(user, chat_id)

                    if not tg_user.user_id:
                        self.tg_client.send_message(chat_id=chat_id, text=f'Привет {user.username or user.first_name}')
                        verification_code = tg_user.generate_verification_code()
                        self.tg_client.send_message(chat_id=chat_id, text=f'Подтвердите, пожалуйста, свой аккаунт. '
                                                                          f'vomit.ga '
                                                                          f'CODE: {verification_code} ')
                    else:
                        self._get_message_authorized_users(item.message, tg_user)

    def _get_message_authorized_users(self, message: Message, tg_user: TgUser):
        user_state = redis_instance.get(tg_user.tg_id)
        if message.text == '/cancel':
            redis_instance.delete(tg_user.tg_id)
            redis_instance.delete(f'{tg_user.tg_id}cat_name')
            self.tg_client.send_message(chat_id=message.chat.id, text='Отмена')
            return
        if user_state in self.commands:
            answer = self.commands[user_state](message=message, tg_user=tg_user)
            self.tg_client.send_message(chat_id=message.chat.id, text=answer)
            return
        if message.text in self.allow_commands_list:
            redis_instance.set(tg_user.tg_id, message.text)
            answer = self.allow_commands_list[message.text](message, tg_user)
            self.tg_client.send_message(chat_id=message.chat.id, text=answer)
            return
        self.tg_client.send_message(chat_id=message.chat.id, text='неизвестная команда')

    def _get_goals(self, message: Message, tg_user: TgUser) -> str:
        user_goals: list[Goal] = Goal.objects.prefetch_related('category').filter(
            Q(category__board__participants__user_id=tg_user.user_id) &
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False)
        )
        goals_list = '\n'.join(f'#{goal.id} {goal.title}' for goal in user_goals)
        redis_instance.delete(tg_user.tg_id)
        return goals_list if goals_list else 'Цели не найдены'

    def _create_category(self, message: Message, tg_user: TgUser):
        self.tg_client.send_message(chat_id=message.chat.id,
                                    text='Введите название категории для создания или /cancel для отмены'
                                    )
        user_categories = GoalCategory.objects.prefetch_related('board__participants__user').filter(
            board__participants__user_id=tg_user.user_id,
            is_deleted=False
        )
        categories_list = '\n'.join(f'#{category.id} {category.title}' for category in user_categories)
        self.tg_client.send_message(chat_id=message.chat.id, text=categories_list)
        redis_instance.set(tg_user.tg_id, 'set_name_category')

    def _set_name_category(self, message: Message, tg_user: TgUser):
        goal_category: list[GoalCategory] = GoalCategory.objects.prefetch_related('board__participants__user').filter(
            Q(board__participants__user_id=tg_user.user_id) &
            Q(is_deleted=False) &
            Q(title__iexact=message.text)
        )
        if goal_category:
            redis_instance.append(f'{tg_user.tg_id}cat_name', goal_category[0].id)
            redis_instance.set(tg_user.tg_id, 'set_name_goal')
            self.tg_client.send_message(chat_id=message.chat.id,
                                        text='Введите название цели для создания или /cancel для отмены')
            return
        self.tg_client.send_message(chat_id=message.chat.id, text='Не верное имя категории попробуйте еще раз')

    def _set_name_goal(self, message: Message, tg_user: TgUser):
        obj = Goal.objects.create(user_id=tg_user.user_id,
                                  title=message.text,
                                  category_id=int(redis_instance.get(f'{tg_user.tg_id}cat_name'))
                                  )
        if obj:
            self.tg_client.send_message(chat_id=message.chat.id, text='Цель создана')
            redis_instance.delete(tg_user.tg_id)
            redis_instance.delete(f'{tg_user.tg_id}cat_name')
            return
        self.tg_client.send_message(chat_id=message.chat.id, text='Что то не то')
