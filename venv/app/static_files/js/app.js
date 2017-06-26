(function(){
    'use_strict'

    angular.module('app', ['ngResource'])
           .controller('MainCtrl', MainCtrl)
           .factory('AccountSvc', AccountSvc)
           .config(Config);


    function MainCtrl($http, $httpParamSerializer, AccountSvc) {
        vm = this;
        vm.client_id = 'bUMXpDJVBUZXRYcVLPd1dbuaoJ2s32mLwA8XquaS';
        vm.userLogin = userLogin;
        vm.userSignUp = userSignUp;
        vm.getUser = getUser;
        vm.getAccessToken = getAccessToken;
        vm.updateUser = updateUser;
        vm.open_addProvider = open_addProvider;
        vm.activateBusinessAccount_popup = activateBusinessAccount_popup;
        vm.activateBusinessAccount_save = activateBusinessAccount_save;
        vm.user = {};

        function userLogin() {
            if (vm.auth.username && vm.auth.password) {
                vm.auth.grant_type = 'password';
                vm.auth.client_id = vm.client_id;
                $http({
                    method: 'POST',
                    url: '/o/token/',
                    headers: { "Content-type": "application/x-www-form-urlencoded; charset=utf-8" },
                    data: $httpParamSerializer(vm.auth)
                }).then(function(response) {
                    Cookies.set('auth_token', response.data.access_token);
                    Cookies.set('ref_token', response.data.refresh_token);

                    location.href = '/home/';
                }).catch(function(error) {
                    
                });
            }
        }

        function userSignUp(user) {
            if(user.first_name && user.last_name && user.username && user.password) {
                $http.post('/signup/', user).then(function(response) {
                    alert('Sign up success! You can now login your account.');
                }).catch(function(error) {

                });
            } else {
                alert('Please input all fields');
            }
        }

        function getUser() {
            vm.loading = true;

            setTimeout(function() {
                $http.get('/api/v1/users/get_user/').then(function (response) {
                    vm.user = angular.copy(response.data.user);
                    vm.loading = false;
                }).catch(function (error) {
                    if (error.status == 401) {
                        // refresh token
                        if(Cookies.get('ref_token'))
                            vm.getAccessToken();

                    } else {
                        console.log(error);
                    }
                });
            }, 1000);
        }
        vm.getUser();

        function updateUser() {
            $http.put('/api/v1/users/update_user/', vm.user).then(function (response) {
                vm.user = angular.copy(response.data.user);
                vm.loading = false;
                console.log(vm.user.first_name);
            }).catch(function (error) {
                if (error.status == 401) {
                    // refresh token
                        if(Cookies.get('ref_token')) {
                            vm.getAccessToken();
                        }
                } else {
                    console.log(error);
                }
            });
        }

        function getAccessToken() {
            req = {
                grant_type: 'refresh_token',
                client_id: vm.client_id,
                refresh_token: Cookies('ref_token') || ''
            }

            $http({
                method: 'POST',
                url: '/o/token/',
                headers: { "Content-type": "application/x-www-form-urlencoded; charset=utf-8" },
                data: $httpParamSerializer(req)
            }).then(function(response) {
                Cookies.set('auth_token', response.data.access_token);
                Cookies.set('ref_token', response.data.refresh_token);
            }).catch(function(error) {

            });
        }

        function activateBusinessAccount_popup() {
            $('#activateBusinessPopup').modal('show');
        }

        function activateBusinessAccount_save(data) {
            
            data.user = vm.user.id;
            data.metadata = {};
            data.metadata['address'] = data.address;
            
            AccountSvc.save(data, function(data) {
                console.log(data);
            }, function(error) {
                console.log(error);
            });
        }

        function open_addProvider() {
            $('#addProvider').modal('show');
        }

        function parseDate(value) {
            return moment(value);
        }
    }

    function Config($interpolateProvider, $httpProvider, $resourceProvider) {
        $interpolateProvider.startSymbol('{$').endSymbol('$}');
        $resourceProvider.defaults.stripTrailingSlashes = false;

        var auth_token = Cookies.get('auth_token');

        if (auth_token) {
            $httpProvider.defaults.headers.common['Authorization'] = 'Bearer ' + auth_token;
        }
    }


    function AccountSvc($resource) {
        return $resource('/api/v1/account/:accountId/', {}, {
            query: {
                method: 'GET',
                isArray: false
            },
            update: {
                method: 'PUT',
                isArray: false
            }
        });
    }
})();