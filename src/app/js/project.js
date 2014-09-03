var module = angular.module('app', ['ngRoute','ngAnimate', 'ui.codemirror', 'CONSTANTS'])
    .config(function($locationProvider, $routeProvider) {
        humane.info = humane.spawn({ 
            addnCls: 'humane-fatty-info', 
            timeout: 2000
        });

        $locationProvider.html5Mode(false);
        $routeProvider
                .when('/view', {
                    templateUrl: 'template/fileview.html', 
                    controller: CtrProjectView
                })
                .otherwise({redirectTo: '/view'});
        
    })
    .run(function($rootScope, $http, CONFIG){
        $rootScope.filelist = [];
        $rootScope.filenavlist = [];
        $rootScope.idactivefile = -1;
        $rootScope.user = JSON.parse(window.localStorage.getItem("user"));
        $rootScope.project = JSON.parse(window.localStorage.getItem("viewproject"));
        
        $http({
            method : 'POST',
            url : CONFIG.url+'getfiles',
            data: {
                iduser : $rootScope.user.id,
                idproject : $rootScope.project.id
            },
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                'di' : window.localStorage.getItem("sk")
            }
        })
        .success(function(data){
            if(data.esit === 1){
                console.log(data);
                for(var i in data.result){
                    $rootScope.filelist.push({
                        id : data.result[i].id,
                        name :  data.result[i].nome,
                        type : parseInt(data.result[i].tipo),
                        text : ""
                    });
                }
            } else {
                humane.info(data.result);
            };
        }).error(function(data){
            console.log(data);
            $rootScope.bSpin = false;
        });
        
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