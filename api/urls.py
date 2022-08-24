from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register('branch', views.BranchViewSet)
router.register('department', views.DepartmentViewSet)
router.register('staff', views.StaffViewSet)
router.register('savingaccount', views.SavingAccountViewSet)
router.register('checkingaccount', views.CheckingAccountViewSet)
router.register('loan', views.LoanViewSet)
router.register('loanrelease', views.LoanReleaseViewSet)
router.register('client', views.ClientViewSet)
router.register('client_branch', views.Client_BranchViewSet)
router.register('client_loan', views.Client_LoanViewSet)

app_name = 'api'
urlpatterns = router.urls
