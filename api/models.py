from django.db import models


VARCHARMAX = 200
MAXDIGITS = 28
DECIMALPLACES = 8


class Branch(models.Model):  # 支行
    name = models.CharField(max_length=VARCHARMAX, primary_key=True)
    city = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    property = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)


class Department(models.Model):  # 部门
    id = models.CharField(max_length=VARCHARMAX, primary_key=True)
    branch_name = models.ForeignKey('Branch', to_field='name', on_delete=models.RESTRICT)
    name = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    type = models.CharField(max_length=VARCHARMAX, null=True, blank=True)


class Staff(models.Model):  # 人员
    id = models.CharField(max_length=VARCHARMAX, primary_key=True)
    department_id = models.ForeignKey('Department', to_field='id', on_delete=models.RESTRICT)
    is_manager = models.BooleanField(null=True, blank=True)
    name = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    phone_number = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    address = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    hiredate = models.DateTimeField(null=True, blank=True)


class SavingAccount(models.Model):  # 储蓄账户
    id = models.CharField(max_length=VARCHARMAX, primary_key=True)
    currency = models.CharField(max_length=VARCHARMAX)
    balance = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)
    interest_rate = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)
    staff_id = models.ForeignKey('Staff', to_field='id', null=True, blank=True, on_delete=models.RESTRICT)
    open_date = models.DateTimeField(null=True, blank=True)
    last_access_date = models.DateTimeField(null=True, blank=True)


class CheckingAccount(models.Model):  # 支票账户
    id = models.CharField(max_length=VARCHARMAX, primary_key=True)
    balance = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)
    overdraft = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)
    staff_id = models.ForeignKey('Staff', to_field='id', null=True, blank=True, on_delete=models.RESTRICT)
    open_date = models.DateTimeField(null=True, blank=True)
    last_access_date = models.DateTimeField(null=True, blank=True)


class Loan(models.Model):  # 贷款
    id = models.CharField(max_length=VARCHARMAX, primary_key=True)
    branch_name = models.ForeignKey('Branch', to_field='name', on_delete=models.RESTRICT)
    total = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)
    balance = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES, default=total)
    staff_id = models.ForeignKey('Staff', to_field='id', null=True, blank=True, on_delete=models.RESTRICT)


class LoanRelease(models.Model):  # 贷款发放
    client_loan_id = models.ForeignKey('Client_Loan', to_field='id', on_delete=models.RESTRICT, default=None)
    release_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=MAXDIGITS, decimal_places=DECIMALPLACES)

    class Meta:
        unique_together = (('client_loan_id', 'release_date'),)


class Client(models.Model):  # 客户
    id = models.CharField(max_length=VARCHARMAX, primary_key=True)
    name = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    phone_number = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    address = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    contact_name = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    contact_email = models.CharField(max_length=VARCHARMAX, null=True, blank=True)
    contact_relationship = models.CharField(max_length=VARCHARMAX, null=True, blank=True)


class Client_Branch(models.Model):  # 客户_支行
    client_id = models.ForeignKey('Client', to_field='id', on_delete=models.RESTRICT)
    branch_name = models.ForeignKey('Branch', to_field='name', on_delete=models.RESTRICT)
    saving_account_id = models.ForeignKey('SavingAccount', to_field='id',
                                          null=True, blank=True, on_delete=models.RESTRICT)
    checking_account_id = models.ForeignKey('CheckingAccount', to_field='id',
                                            null=True, blank=True, on_delete=models.RESTRICT)

    class Meta:
        unique_together = (('client_id', 'branch_name'),)


class Client_Loan(models.Model):  # 客户_贷款
    client_id = models.ForeignKey('Client', to_field='id', on_delete=models.RESTRICT)
    loan_id = models.ForeignKey('Loan', to_field='id', on_delete=models.RESTRICT)

    class Meta:
        unique_together = (('client_id', 'loan_id'),)
