function CtrProjects($rootScope, $scope, $http, CONFIG){
    $rootScope.bSpin = true;
    
    $scope.listproject = [];
    
    $http({
        method : 'POST',
        url : CONFIG.url+'getprojects',
        data : {iduser : JSON.parse(window.localStorage.getItem("user")).id},
        transformRequest : param,
        headers : {
            'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
            'di' : window.localStorage.getItem("sk")
        }
    })
    .success(function(data){
        if(data.esit === 1){
            $scope.listproject = data.result;
        } else {
            humane.info(data.result);
        };
        $rootScope.bSpin = false;
    }).error(function(data){
        console.log(data);
        $rootScope.bSpin = false;
    });
    
    $scope.viewproject = function(project){
        window.localStorage.setItem("viewproject", JSON.stringify(project));
        window.location.href = "project.html";
    };
};

function CtrProjectsCreate($rootScope, $scope, $http, CONFIG){
    $scope.create = function(){
        if(typeof $scope.nameproject === "undefined" || $scope.nameproject.trim() === ""){
            humane.info("Error!!! Empty Fields");
            return;
        }
        
        $http({
            method : 'POST',
            url : CONFIG.url+'createproject',
            data : {
                iduser : JSON.parse(window.localStorage.getItem("user")).id,
                nome : $scope.nameproject
            },
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                'di' : window.localStorage.getItem("sk")
            }
        })
        .success(function(data){
            if(data.esit === 1){
                window.location.hash = "#/projects";
            } else {
                humane.info(data.result);
            };
            $rootScope.bSpin = false;
        }).error(function(data){
            console.log(data);
            $rootScope.bSpin = false;
        });
        
    };
};

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