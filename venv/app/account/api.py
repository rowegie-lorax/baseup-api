from .serializer import UserSerializer, ServiceSerializer, ProviderSerializer, AccountSerializer
from .models import User, Provider, Service, Account
from .permissions import IsAdmin

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import detail_route, list_route

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope, OAuth2Authentication

import json

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAdmin, TokenHasReadWriteScope, ]
    required_scopes = ['write', 'read']
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        users = self.get_queryset()

        return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        try:
            user = request.user
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.email = request.data['email']
            user.address = request.data['address']
            user.save()
        except Exception as e:
            return Response('Error:' + str(e), status=status.HTTP_400_INVALID_REQUEST)

        return Response({'user': UserSerializer(user).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk).delete
        except Exception as e:
            return Response('Error:' + str(e), status=status.HTTP_400_INVALID_REQUEST)
        
        return Response('Deleted Successfully', status=status.HTTP_200_OK)
    
    @list_route()
    def get_user(self, request):
        user = UserSerializer(request.user).data

        user['is_business'] = False
        user['account'] = {}
        try:
            account = Account.objects.get(user=request.user)
            user['is_business'] = True
            user['account'] = AccountSerializer(account).data

            user['account']['metadata'] = json.dumps(account.metadata)
        except Exception as e:
            pass

        return Response({'user': user}, status=status.HTTP_200_OK)


class ServiceViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAdmin, TokenHasReadWriteScope, ]
    required_scopes = ['write', 'read']
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def list(self, request):
        services = self.get_queryset()

        return Response(ServiceSerializer(services, many=True).data,
                        status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return super(ServiceViewSet, self).create(request, *args, **kwargs)

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


class ProviderViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAdmin, TokenHasReadWriteScope, ]
    required_scopes = ['write', 'read']
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    def list(self, request):
        providers = self.get_queryset()

        return Response(ProviderSerializer(providers, many=True).data,
                        status=status.HTTP_200_OK)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


class AccountViewSet(viewsets.ModelViewSet):
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAdmin, TokenHasReadWriteScope, ]
    required_scopes = ['write', 'read']
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request):
        accounts = self.get_queryset()

        return Response(AccountSerializer(accounts, many=True).data,
                        status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            account = Account()
            account.name = request.data['name']
            account.metadata = request.data['metadata']
            account.user = User.objects.get(pk=request.data['user'])
            account.save()

            return Response(AccountSerializer(account).data,
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response('Error:' + str(e), status=status.HTTP_400_INVALID_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        return super(AccountViewSet, self).update(request, pk, *args, **kwargs)

    def destroy(self, request, pk=None, *args, **kwargs):
        return super(AccountViewSet, self).destroy(request, pk, *args, **kwargs)
