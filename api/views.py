from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone

import random
from decimal import Decimal

from .serializers import *


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'name'

    @action(detail=False, methods=['post'])
    def statistics(self, request):
        radio = request.data.get('radio')

        now = timezone.now()
        # 本年
        saving_accounts = SavingAccount.objects.filter(currency='人民币', open_date__year=now.year)
        checking_accounts = CheckingAccount.objects.filter(open_date__year=now.year)
        loan_releases = LoanRelease.objects.filter(release_date__year=now.year)
        if radio == '本季':
            month_low = ((now.month - 1) // 3) * 3 + 1
            month_high = ((now.month - 1) // 3) * 3 + 3
            saving_accounts = saving_accounts.filter(open_date__month__gte=month_low,
                                                     open_date__month__lte=month_high)
            checking_accounts = checking_accounts.filter(open_date__month__gte=month_low,
                                                         open_date__month__lte=month_high)
            loan_releases = loan_releases.filter(release_date__month__gte=month_low,
                                                 release_date__month__lte=month_high)
        elif radio == '本月':
            saving_accounts = saving_accounts.filter(open_date__month=now.month)
            checking_accounts = checking_accounts.filter(open_date__month=now.month)
            loan_releases = loan_releases.filter(release_date__month=now.month)

        data = []
        branches = Branch.objects.all()
        for branch in branches:
            data.append({
                'branch_name': branch.name,
                'saving_account_num': 0,
                'savings': 0,
                'checking_account_num': 0,
                'checking_savings': 0,
                'loan_amount': 0
            })
            for client_branch in Client_Branch.objects.filter(branch_name=branch.name):
                try:
                    saving_account = saving_accounts.get(id=client_branch.saving_account_id_id)
                    data[-1]['saving_account_num'] += 1
                    data[-1]['savings'] += saving_account.balance
                except SavingAccount.DoesNotExist:
                    pass
                try:
                    checking_account = checking_accounts.get(id=client_branch.checking_account_id_id)
                    data[-1]['checking_account_num'] += 1
                    data[-1]['checking_savings'] += checking_account.balance
                except CheckingAccount.DoesNotExist:
                    pass
            for loan in Loan.objects.filter(branch_name=branch.name):
                for client_loan in Client_Loan.objects.filter(loan_id=loan.id):
                    for loan_release in loan_releases.filter(client_loan_id=client_loan.id):
                        data[-1]['loan_amount'] += loan_release.amount

        return Response(status=status.HTTP_200_OK, data=data)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'


class SavingAccountViewSet(viewsets.ModelViewSet):
    queryset = SavingAccount.objects.all()
    serializer_class = SavingAccountSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        saving_account_id = request.data.get('saving_account_id')
        currency = request.data.get('currency')
        balance = request.data.get('balance')
        interest_rate = request.data.get('interest_rate')
        staff_id = request.data.get('staff_id')

        staff = None
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='负责人身份证号错误')

        try:
            saving_account = SavingAccount.objects.get(id=saving_account_id)
        except SavingAccount.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='储蓄账户号错误')

        saving_account.currency = currency
        saving_account.balance = balance
        saving_account.interest_rate = interest_rate
        if staff:
            saving_account.staff_id = staff
        saving_account.last_access_date = timezone.now()
        try:
            saving_account.save()
            return Response(status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='更新保存错误')

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        saving_account = self.get_object()
        sid = transaction.savepoint()
        try:
            # 先删除client_branch中的外键
            client_branch = Client_Branch.objects.get(saving_account_id=saving_account.id)
            client_branch.saving_account_id = None
            client_branch.save()
        except Client_Branch.DoesNotExist or IntegrityError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='删除client_branch外键失败')

        try:
            saving_account.delete()
        except ProtectedError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='删除账户失败')

        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckingAccountViewSet(viewsets.ModelViewSet):
    queryset = CheckingAccount.objects.all()
    serializer_class = CheckingAccountSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        checking_account_id = request.data.get('checking_account_id')
        balance = request.data.get('balance')
        overdraft = request.data.get('overdraft')
        staff_id = request.data.get('staff_id')

        staff = None
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='负责人身份证号错误')

        try:
            checking_account = CheckingAccount.objects.get(id=checking_account_id)
        except CheckingAccount.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='支票账户号错误')

        checking_account.balance = balance
        checking_account.overdraft = overdraft
        if staff:
            checking_account.staff_id = staff
        checking_account.last_access_date = timezone.now()
        checking_account.save()
        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        sid = transaction.savepoint()
        checking_account = self.get_object()
        try:
            # 先删除client_branch中的外键
            client_branch = Client_Branch.objects.get(checking_account_id=checking_account.id)
            client_branch.checking_account_id = None
            client_branch.save()
        except Client_Branch.DoesNotExist or IntegrityError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='删除client_branch外键失败')

        try:
            checking_account.delete()
        except ProtectedError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='删除账户失败')

        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def create_loan(self, request):
        total = Decimal(request.data.get('total'))
        branch_name = request.data.get('branch_name')
        staff_id = request.data.get('staff_id')
        clients = request.data.get('clients')
        clients = [dict(t) for t in {tuple(d.items()) for d in clients}]  # 去重
        if total <= 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='贷款总额需大于0')
        elif len(clients) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='贷款人数需大于0')
        # 检查支行是否存在
        try:
            branch = Branch.objects.get(name=branch_name)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=f'支行名错误')
        # 检查client是否都存在
        for client in clients:
            try:
                client['instance'] = Client.objects.get(id=client['id'])
            except Client.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=f'客户{client["id"]}不存在')
        # 检查staff是否存在
        staff = None
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=f'员工{staff_id}不存在')
        # 新建Loan
        sid = transaction.savepoint()
        max_rand_id_time = 10
        random.seed()
        new_loan = None
        for _ in range(max_rand_id_time):
            loan_id = str(random.randint(0, 999999999999)).zfill(12)
            try:
                new_loan = Loan.objects.create(
                    id=loan_id,
                    branch_name=branch,
                    total=total,
                    balance=total,
                    staff_id=staff
                )
                break
            except IntegrityError:
                continue
        if not new_loan:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=f'新建贷款失败，请重试')
        # 创建client_loan
        try:
            for client in clients:
                Client_Loan.objects.create(client_id=client['instance'], loan_id=new_loan)
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=f'新建贷款失败，请重试')

    def update(self, request, *args, **kwargs):
        loan_id = request.data.get('loan_id')
        staff_id = request.data.get('staff_id')

        if not staff_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='负责人身份证号未填写')
        else:
            try:
                loan = Loan.objects.get(id=loan_id)
            except Loan.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='贷款号错误')
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='负责人身份证号错误')
            if loan.staff_id:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='已有负责人不允许修改')
            else:
                loan.staff_id = staff
                loan.save()
                return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def release_loan(self, request):
        loan_id = request.data.get('loan_id')
        clients = request.data.get('clients')
        # 查询余额
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='贷款号错误')
        if loan.balance <= 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='该贷款已发放完成')
        release_sum = 0
        for client in clients:
            client['amount'] = Decimal(client['amount'])
            release_sum += client['amount']
        if release_sum == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='发放额不能为0')
        elif release_sum > loan.balance:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='发放额超过余额')
        # 查询发放人员是否都与该贷款关联
        for client in clients:
            try:
                client['client_loan'] = Client_Loan.objects.get(loan_id=loan_id, client_id=client['id'])
            except Client_Loan.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='有客户不是该贷款发放对象')
        # 发放
        sid = transaction.savepoint()
        loan.balance -= release_sum
        loan.save()
        now = timezone.now()
        try:
            for client in clients:
                if client['amount'] > 0:
                    LoanRelease.objects.create(
                        client_loan_id=client['client_loan'],
                        release_date=now,
                        amount=client['amount']
                    )
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_200_OK)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='发放失败')

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        loan = self.get_object()
        if loan.balance != 0 and loan.balance != loan.total:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='正在发放的贷款不允许删除')
        # 查询所有Client_Loan
        client_loans = Client_Loan.objects.filter(loan_id=loan.id)

        sid = transaction.savepoint()
        try:
            for client_loan in client_loans:
                # 先删除引用了client_loan的LoanRelease记录
                LoanRelease.objects.filter(client_loan_id=client_loan.id).delete()
            # 再删除所有的client_loan
            client_loans.delete()
            # 最后删除loan本身
            loan.delete()
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='删除LoanRelease或Loan失败')

class LoanReleaseViewSet(viewsets.ModelViewSet):
    queryset = LoanRelease.objects.all()
    serializer_class = LoanReleaseSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        text_fields = ['id', 'name', 'phone_number', 'address', 'contact_name', 'contact_phone_number',
                       'contact_email', 'contact_relationship']
        queryset = self.queryset
        for text_field in text_fields:  # 与查询, 更复杂的查询可以通过django.db.models.Q实现
            query_param = self.request.query_params.get(text_field)
            if query_param:
                queryset = queryset.filter(**{f'{text_field}__icontains': query_param})
        return queryset


class Client_BranchViewSet(viewsets.ModelViewSet):
    queryset = Client_Branch.objects.all()
    serializer_class = Client_BranchSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        related_fields = ['client_id', 'branch_name', 'saving_account_id']
        queryset = self.queryset
        for related_field in related_fields:
            query_param = self.request.query_params.get(related_field)
            if query_param:
                queryset = queryset.filter(
                    **{f'{related_field}__{related_field.split("_")[-1]}__icontains': query_param}
                )
        return queryset

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def open_saving_account(self, request):
        # 查询用户的Client_Branch实例是否存在, 若不存在则创建, 若存在且已经有saving_account_id则开户失败
        client_id = request.data.get('client_id')
        branch_name = request.data.get('branch_name')
        currency = request.data.get('currency')
        interest_rate = request.data.get('interest_rate')
        staff_id = request.data.get('staff_id')

        if not (client_id and branch_name and currency and interest_rate):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='所需字段不完整')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='客户不存在')

        try:
            branch = Branch.objects.get(name=branch_name)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='支行不存在')

        staff = None
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='员工不存在')

        sid = transaction.savepoint()

        try:
            client_branch = Client_Branch.objects.get(client_id=client_id, branch_name=branch_name)
            if client_branch.saving_account_id:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='客户在该支行已有储蓄账户')
        except Client_Branch.DoesNotExist:
            try:
                client_branch = Client_Branch.objects.create(client_id=client, branch_name=branch)
            except IntegrityError:
                transaction.savepoint_rollback(sid)
                return Response(status=status.HTTP_400_BAD_REQUEST, data='客户与支行建立联系失败')

        # 创建储蓄账户
        max_rand_id_time = 10
        random.seed()
        new_account = None
        for _ in range(max_rand_id_time):
            account_id = str(random.randint(0, 999999999999)).zfill(12)
            try:
                now = timezone.now()
                new_account = SavingAccount.objects.create(
                    id=account_id,
                    currency=currency,
                    balance=0,
                    interest_rate=interest_rate,
                    staff_id=staff,
                    open_date=now,
                    last_access_date=now
                )
                break
            except IntegrityError:
                continue
        if not new_account:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='创建账户失败, 请重试')

        try:
            #  账户与客户关联
            client_branch.saving_account_id = new_account
            client_branch.save()
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def open_checking_account(self, request):
        # 查询用户的Client_Branch实例是否存在, 若不存在则创建, 若存在且已经有checking_account_id则开户失败
        client_id = request.data.get('client_id')
        branch_name = request.data.get('branch_name')
        overdraft = request.data.get('overdraft')
        staff_id = request.data.get('staff_id')

        if not (client_id and branch_name and overdraft):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='所需字段不完整')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='客户不存在')

        try:
            branch = Branch.objects.get(name=branch_name)
        except Branch.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='支行不存在')

        staff = None
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='员工不存在')

        sid = transaction.savepoint()

        try:
            client_branch = Client_Branch.objects.get(client_id=client_id, branch_name=branch_name)
            if client_branch.checking_account_id:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='客户在该支行已有支票账户')
        except Client_Branch.DoesNotExist:
            try:
                client_branch = Client_Branch.objects.create(client_id=client, branch_name=branch)
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='客户与支行建立联系失败')

        # 创建储蓄账户
        max_rand_id_time = 10
        random.seed()
        new_account = None
        for _ in range(max_rand_id_time):
            account_id = str(random.randint(0, 999999999999)).zfill(12)
            try:
                now = timezone.now()
                new_account = CheckingAccount.objects.create(
                    id=account_id,
                    balance=0,
                    overdraft=overdraft,
                    staff_id=staff,
                    open_date=now,
                    last_access_date=now
                )
                break
            except IntegrityError:
                continue
        if not new_account:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='创建账户失败, 请重试')

        try:
            #  账户与客户关联
            client_branch.checking_account_id = new_account
            client_branch.save()
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            return Response(status=status.HTTP_400_BAD_REQUEST, data='账户与客户关联失败')


class Client_LoanViewSet(viewsets.ModelViewSet):
    queryset = Client_Loan.objects.all()
    serializer_class = Client_LoanSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_queryset(self):
        related_fields = ['client_id', 'loan_id']
        queryset = self.queryset
        for related_field in related_fields:
            query_param = self.request.query_params.get(related_field)
            if query_param:
                queryset = queryset.filter(
                    **{f'{related_field}__{related_field.split("_")[-1]}__icontains': query_param}
                )
        return queryset
