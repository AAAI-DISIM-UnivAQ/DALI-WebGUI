var module = angular.module('app', ['ngRoute','ngAnimate', 'CONSTANTS']).
    config(function($locationProvider, $routeProvider) {
        humane.info = humane.spawn({ 
            addnCls: 'humane-fatty-info', 
            timeout: 2000
        });
        $locationProvider.html5Mode(false);
        $routeProvider
                .when('/login', {
                    templateUrl: 'template/login.html', 
                    controller: CtrLogin
                })
                .otherwise({redirectTo: '/login'});
    });