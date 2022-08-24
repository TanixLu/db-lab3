from django.contrib import admin

from .models import *

admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Staff)
admin.site.register(SavingAccount)
admin.site.register(CheckingAccount)
admin.site.register(Loan)
admin.site.register(LoanRelease)
admin.site.register(Client)
admin.site.register(Client_Branch)
admin.site.register(Client_Loan)

