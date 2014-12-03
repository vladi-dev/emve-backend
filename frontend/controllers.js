var emweApp = angular.module('emweApp', []);
var host = 'http://127.0.0.1:5000';
var host = 'http://amwe.herokuapp.com';

emweApp.controller('RegisterCtrl', function ($scope, $http, $window) {
    $scope.registerMe = function () {
        $http.post(host + '/register', $scope.register)
            .success(function (data, status, headers, config) {
                alert(1)
            })
            .error(function (data, status, headers, config) {
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
        $http.post(host + '/auth', $scope.login)
            .success(function (data, status, headers, config) {
                $window.sessionStorage.token = data.token;
                $scope.token = $window.sessionStorage.token;
            })
            .error(function (data, status, headers, config) {
                $scope.data = data
                $scope.status = status
                $scope.headers = headers
                $scope.config = config

                delete $window.sessionStorage.token;
            });
    }
});


emweApp.controller('CategoryListCtrl', function ($scope, $http) {
    $scope.getCategories = function () {
        $http.get(host + '/api/category').success(function (data) {
            $scope.categories = data.categories;
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

emweApp.config(function ($httpProvider) {
    $httpProvider.interceptors.push('authInterceptor');
});