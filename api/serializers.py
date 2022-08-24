from rest_framework import serializers
from .models import *
import re


class BranchSerializer(serializers.ModelSerializer):
    url_field_name = 'name'
    url = serializers.HyperlinkedIdentityField(view_name='api:branch-detail', lookup_field='name', read_only=True)

    class Meta:
        model = Branch
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:department-detail', lookup_field='id', read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:staff-detail', lookup_field='id', read_only=True)

    class Meta:
        model = Staff
        fields = '__all__'


class SavingAccountSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:savingaccount-detail', lookup_field='id', read_only=True)

    class Meta:
        model = SavingAccount
        fields = '__all__'


class CheckingAccountSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:checkingaccount-detail', lookup_field='id', read_only=True)

    class Meta:
        model = CheckingAccount
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:loan-detail', lookup_field='id', read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'


class LoanReleaseSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:loanrelease-detail', lookup_field='id', read_only=True)

    class Meta:
        model = LoanRelease
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:client-detail', lookup_field='id', read_only=True)

    class Meta:
        model = Client
        fields = '__all__'

    def validate_id(self, client_id):
        client_id = client_id.upper()
        if len(client_id) != 18:
            raise serializers.ValidationError("client id length error")
        id_pattern = r'(^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}' \
                     r'[0-9X]$)|(^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}$)'
        if not re.match(id_pattern, client_id):
            raise serializers.ValidationError('client id did not pass verification')
        factor = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        last_char = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        id_sum = 0
        for i in range(0, 17):
            id_sum += int(client_id[i]) * factor[i]
        id_sum %= 11
        if (last_char[id_sum]) != str(client_id[17]):
            raise serializers.ValidationError('client id did not pass verification')
        return client_id


class Client_BranchSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:client_branch-detail', lookup_field='id', read_only=True)

    class Meta:
        model = Client_Branch
        fields = '__all__'


class Client_LoanSerializer(serializers.ModelSerializer):
    url_field_name = 'id'
    url = serializers.HyperlinkedIdentityField(view_name='api:client_loan-detail', lookup_field='id', read_only=True)

    class Meta:
        model = Client_Loan
        fields = '__all__'
