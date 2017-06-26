from rest_framework import serializers

from .models import User, Provider, Service, Account


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'address',
                  'city', 'country', 'province', 'postal_code',
                  'timezone', 'phone', 'alt_phone', 'is_staff', 'is_admin')


class ServiceSerializer(serializers.ModelSerializer):
    
    class Meta:
    	model = Service
    	fields = ('id', 'name', 'desc', 'cost', 'duration', 'max_customers')


class ProviderSerializer(serializers.ModelSerializer):
	service = ServiceSerializer()

	class Meta:
		model = Provider
		fields = ('id', 'first_name', 'last_name', 'email', 'avatar',
              'services', 'phone', 'status')


class AccountSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Account
        fields = ('id', 'name', 'user', 'metadata', 'create_at', 'update_at')
