var module = angular.module('app', ['ngRoute','ngAnimate', 'CONSTANTS']).
    config(function($locationProvider, $routeProvider) {
        humane.info = humane.spawn({ 
            addnCls: 'humane-fatty-info', 
            timeout: 2000
        });
        $locationProvider.html5Mode(false);
        $routeProvider
                .when('/projects', {
                    templateUrl: 'template/projects.html', 
                    controller: CtrProjects
                })
                .when('/projects/create', {
                    templateUrl: 'template/projects_create.html', 
                    controller: CtrProjectsCreate
                })
                .otherwise({redirectTo: '/projects'});
    })
    .run(function($rootScope, $http, CONFIG){
        $rootScope.logout = function(){
            $rootScope.bSpin = true;

            $http({
                method : 'POST',
                url : CONFIG.url+'logout',
                transformRequest : param,
                headers : {
                    'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                    'di' : window.localStorage.getItem("sk")
                }
            })
            .success(function(data){
                if(data.esit === 1){
                    window.localStorage.clear();
                    window.location.href = "index.html";
                } else {
                    humane.info(data.result);
                };
            }).error(function(data){
                console.log(data);
                $rootScope.bSpin = false;
            });
        };
    });
    
param = function (e){
    var data = "";
    var first = true;
    for(var i in e){
        if(first){
            first = false;
        } else {
            data += "&";
        }
        data += i+"="+e[i];
    }
    return data;
};