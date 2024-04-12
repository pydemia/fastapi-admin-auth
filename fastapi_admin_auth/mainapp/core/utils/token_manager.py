from datetime import datetime, timedelta

from autologging import logged
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from corusadmin.llm.models import (
    TokenPolicy,
    TokenAmountUsed
)
from corusadmin.chat.models import (
    Chat,
    ChatMessage
)
from corusadmin.code.models import CodeRequestHistory


__all__ = [
    "TokenManager",
]


@logged
class TokenManager:
    def __init__(self, user: User):
        self.user = user

    def tokens_used_today(self,
                          n: datetime,
                          scope: int,
                          policy: TokenPolicy) -> bool:
        used_tokens: int = 0
        y = n - timedelta(days=1)

        self.__log.info(f"max_token={policy.max_token}")

        date_from = datetime(year=n.year,
                             month=n.month,
                             day=n.day)
        date_to = datetime(year=n.year,
                           month=n.month,
                           day=n.day,
                           hour=23,
                           minute=59,
                           second=59)
        # Chat
        chats = Chat.objects.filter(user_id=self.user.id)
        for chat in chats:
            messages = ChatMessage.objects.filter(
                created_at__gte=date_from,
                created_at__lte=date_to,
                chat_id=chat.conv_id
            )
            for message in messages:
                used_tokens += message.token_count
        # Code
        code_request_history = CodeRequestHistory.objects.filter(
            created_at__gte=date_from,
            created_at__lte=date_to
        )
        for code_request in code_request_history:
            # self.__log.info(f"code_request={code_request}")

            if code_request.result is not None and len(code_request.result) > 0:
                # result = json.loads(code_request.result)  # 생각과는 달리 dict로 smart하게 반환
                result = code_request.result

                if 'usage' in result and 'total_tokens' in result['usage']:
                    used_tokens += result['usage']['total_tokens']

        token_amount_used = TokenAmountUsed.objects.filter(
            scope=scope,
            name=policy.name,
            exec_date=y.strftime("%Y%m%d")
        )

        for t in token_amount_used:
            used_tokens += t.used_token

        self.__log.info(f"used_tokens={used_tokens}, max_token={policy.max_token}")

        if policy.max_token < used_tokens:
            return False
        else:
            return True

    def check_token_availability(self) -> bool:
        """
        가용 token 확인, Policy 없으면 True 리턴
        1.policy 조회(scope: 2(User) > 1(Group) > 0(All))
        """
        n = datetime.now()
        # Policy 조회(User)
        user_policy = TokenPolicy.objects.filter(
            scope=2,
            name=self.user.email
        )
        for policy in user_policy:
            r = self.tokens_used_today(n=n, scope=2, policy=policy)
            if r is False:
                return False
        # Policy 조회(Group)
        for g in self.user.groups.all():
            group_policy = TokenPolicy.objects.filter(
                scope=1,
                name=g.name
            )
            for policy in group_policy:
                r = self.tokens_used_today(n=n, scope=1, policy=policy)
                if r is False:
                    return False
        # Policy 조회(All)
        all_policy = TokenPolicy.objects.filter(
            scope=0
        )
        for policy in all_policy:
            r = self.tokens_used_today(n=n, scope=0, policy=policy)
            if r is False:
                return False
        return True

    async def acheck_token_availability(self) -> bool:
        """
        가용 token 확인, Policy 없으면 True 리턴
        1.policy 조회(scope: 2(User) > 1(Group) > 0(All))
        """
        n = datetime.now()
        # Policy 조회(User)
        user_policy = sync_to_async(TokenPolicy.objects.filter)(
            scope=2,
            name=self.user.email
        )
        for policy in user_policy:
            r = self.tokens_used_today(n=n, scope=2, policy=policy)
            if r is False:
                return False
        # Policy 조회(Group)
        for g in self.user.groups.all():
            group_policy = sync_to_async(TokenPolicy.objects.filter)(
                scope=1,
                name=g.name
            )
            for policy in group_policy:
                r = self.tokens_used_today(n=n, scope=1, policy=policy)
                if r is False:
                    return False
        # Policy 조회(All)
        all_policy = sync_to_async(TokenPolicy.objects.filter)(
            scope=0
        )
        for policy in all_policy:
            r = self.tokens_used_today(n=n, scope=0, policy=policy)
            if r is False:
                return False
        return True

    async def acheck_token_availability(self) -> bool:
        """
        가용 token 확인
        """
        self.__log.info(f"groups={self.user.groups}")
        return True
