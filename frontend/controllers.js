var emweApp = angular.module('emweApp', []);
var host = 'http://emve.dev:5000/api';
var host = 'http://emve.herokuapp.com/api';

emweApp.controller('RegisterCtrl', function ($scope, $http, $window) {
    $scope.registerMe = function () {
        $http.post(host + '/register', $scope.register)
            .success(function (data, status, headers, config) {
                         alert(1)
                     })
            .error(function (data, status, headers, config) {
                       $scope.login_error = data.errors['username'];
                       $scope.data = data
                       $scope.status = status
                       $scope.headers = headers
                       $scope.config = config

                       delete $window.sessionStorage.token;
                   });
    }
});

emweApp.controller('BodyCtrl', function ($scope, $http, $window) {
    $scope.token = $window.sessionStorage.token;
    $scope.loginMe = function () {
        $http.post(host + '/login', $scope.login)
            .success(function (data, status, headers, config) {
                         $window.sessionStorage.token = data.token;
                         $scope.token = $window.sessionStorage.token;
                     })
            .error(function (data, status, headers, config) {
                       $scope.data = data;
                       $scope.status = status;
                       $scope.headers = headers;
                       $scope.config = config;

                       delete $window.sessionStorage.token;
                   });
    }
});


emweApp.controller('CategoryListCtrl', function ($scope, $http) {
    $scope.getCategories = function () {
        $http.get(host + '/category').success(function (data) {
            $scope.categories = data.categories;
        });
    }
});


emweApp.controller('EstablishmentListCtrl', function ($scope, $http) {
    $scope.getEstablishments = function () {
        $http.get(host + '/establishment/2').success(function (data) {
            $scope.establishments = data.establishments;
        });
    }
});

emweApp.factory('authInterceptor', function ($rootScope, $q, $window) {
    return {
        request: function (config) {
            config.headers = config.headers || {};
            if ($window.sessionStorage.token) {
                config.headers.Authorization = 'Bearer ' + $window.sessionStorage.token;
            }
            return config;
        },
        response: function (response) {
            if (response.status === 401) {
                // handle the case where the user is not authenticated
            }
            return response || $q.when(response);
        }
    };
});

emweApp.controller('DeliveryCtl', function ($scope, $http, $window) {

    $scope.makeOrder = function () {
        $http.post(host + '/delivery', $scope.delivery)
            .success(function (data, status, headers, config) {
                         alert(1);
                     })
            .error(function (data, status, headers, config) {
                       $scope.data = data;
                       $scope.status = status;
                       $scope.headers = headers;
                       $scope.config = config;
                   });
    }
});

emweApp.config(function ($httpProvider) {
    $httpProvider.interceptors.push('authInterceptor');
});