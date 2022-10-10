"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token


from core.views import HelloView, PositionView, PackageAddView, PackagesView, BoardsView, PackagesCloseView, BoardsWidthView, ClosedPackagesView, PackagesOpenView, PackagesUnfinishView, UnfinishedPackagesView, PrintLabel

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  
    # username=joe, password=12345678, token=578a9a2d280275b92458ef8dbbf39efb9431b52b
    
    path('position/', PositionView.as_view(), name='position'),
    path('package_add/', PackageAddView.as_view(), name='package_add'),
    path('packages/', PackagesView.as_view(), name='packages'),
    path('boards/', BoardsView.as_view(), name='boards'),
    path('boards_width/', BoardsWidthView.as_view(), name='boards_width'),
    path('packages_close/', PackagesCloseView.as_view(), name='packages_close'),
    path('packages_open/', PackagesOpenView.as_view(), name='packages_open'),
    path('closed_packages/', ClosedPackagesView.as_view(), name='closed_packages'),
    path('packages_unfinish/', PackagesUnfinishView.as_view(), name='packages_unfinish'),
    path('unfinished_packages/', UnfinishedPackagesView.as_view(), name='unfinished_packages'),
    path('print_label/', PrintLabel.as_view(), name='print_label'),
]
