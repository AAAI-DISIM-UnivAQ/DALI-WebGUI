function CtrLogin($rootScope, $scope, $http, CONFIG){
    $rootScope.bSpin = false;
    $scope.priorita = 3;

    $scope.signin = function(){
        var data = {
            username : $scope.usernameLog,
            password : $scope.passwordLog
        };
        
        $http({
            method : 'POST',
            url : CONFIG.url+'login',
            data : data, 
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'"
            }
        })
            .success(function(data){
                if(data.esit === 1){
                    humane.info("Signin success");
                    var user = {
                        id : data.result.id,
                        username : data.result.username,
                        email : data.result.email
                    };
                    window.localStorage.setItem("user", JSON.stringify(user));
                    window.localStorage.setItem("sk", data.result.sk);
                    window.location.href = "dashboard.html";
                } else {
                    alert(data.result);
                };
            }).error(function(data){
                console.log(data);
                $rootScope.bSpin = false;
            });
    };
    
    $scope.signup = function(){
        if($scope.passwordReg !== $scope.repeatpasswordReg){
            humane.info("Le password non corrispondono");
        }
        $rootScope.bSpin = true;
        var data = {
            username : $scope.usernameReg,
            password : $scope.passwordReg,
            email : $scope.emailReg
        };
        
        $http({
            method : 'POST',
            url : CONFIG.url+'register',
            data : data, 
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'"
            }
        })
            .success(function(data){
                if(data.esit === 1){
                    humane.info("Register success");
                    var user = {
                        id : data.result.id,
                        username : data.result.username,
                        email : data.result.email
                    };
                    window.localStorage.setItem("user", JSON.stringify(user));
                    window.localStorage.setItem("sk", data.result.sk);
                    window.location.href = "dashboard.html";
                } else {
                    alert(data.result);
                };
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
    console.log(data);
    return data;
};