function CtrProjectView($rootScope, $scope, $http, CONFIG){
    $scope.activefile = {id:-1, name:"", type:0, text:""};

    $scope.heightEditor = window.innerHeight - 115;
    
    $scope.editorOptions = {
        lineWrapping : true,
        lineNumbers: true
    };
    
    $scope.runfile = function(){
        $http({
            method : 'POST',
            url : CONFIG.url+'runfile',
            data: {
                iduser : $rootScope.user.id,
                idproject : $rootScope.project.id,
                idfile : $scope.activefile.id
            },
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                'di' : window.localStorage.getItem("sk")
            }
        })
        .success(function(data){
            if(data.esit === 1){
                humane.info("File Runned");
            } else {
                humane.info(data.result);
                $rootScope.bSpin = false;
            };
        }).error(function(data){
            console.log(data);
            $rootScope.bSpin = false;
        });
    };
    
    $scope.stopfile = function(){
        $http({
            method : 'POST',
            url : CONFIG.url+'stopfile',
            data: {
                iduser : $rootScope.user.id,
                idproject : $rootScope.project.id,
                idfile : $scope.activefile.id
            },
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                'di' : window.localStorage.getItem("sk")
            }
        })
        .success(function(data){
            if(data.esit === 1){
                humane.info("File Stopped");
            } else {
                humane.info(data.result);
                $rootScope.bSpin = false;
            };
        }).error(function(data){
            console.log(data);
            $rootScope.bSpin = false;
        });
    };
    
    $scope.savefile = function(){
        if(typeof $scope.activefile.text === "undefined" || $scope.activefile.text.trim() == ""){
            humane.info("File empty");
            return;
        }
        $http({
            method : 'POST',
            url : CONFIG.url+'savefile',
            data: {
                iduser : $rootScope.user.id,
                idproject : $rootScope.project.id,
                idfile : $scope.activefile.id,
                text : $scope.activefile.text
            },
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                'di' : window.localStorage.getItem("sk")
            }
        })
        .success(function(data){
            if(data.esit === 1){
                humane.info("File Saved");
            } else {
                humane.info(data.result);
                $rootScope.bSpin = false;
            };
        }).error(function(data){
            console.log(data);
            $rootScope.bSpin = false;
        });
    };
    
    window.onresize = function(){
        $scope.heightEditor = window.innerHeight - 115;
    };
    
    
    
//    gestione della visualizzazione dei file
    $rootScope.openfile = function(id){
        var file;
        if(!isInArrayById($rootScope.filenavlist,id)){
            $rootScope.bSpin = true;
            if($rootScope.idactivefile !== -1){
                updateElementById($rootScope.filenavlist, $rootScope.idactivefile, $scope.activefile.text);
            }
            file = getElementById($rootScope.filelist, id);
            $http({
                method : 'POST',
                url : CONFIG.url+'getfile',
                data: {
                    iduser : $rootScope.user.id,
                    idproject : $rootScope.project.id,
                    idfile : id
                },
                transformRequest : param,
                headers : {
                    'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                    'di' : window.localStorage.getItem("sk")
                }
            })
            .success(function(data){
                console.log(data);
                if(data.esit === 1){
                    file.text = data.result.text;
                    $rootScope.filenavlist.push(file);
                    $rootScope.idactivefile = id;
        
                    switchfile(file);
                    $rootScope.bSpin = false;
                } else {
                    humane.info(data.result);
                    $rootScope.bSpin = false;
                };
            }).error(function(data){
                console.log(data);
                $rootScope.bSpin = false;
            });
        } else {
            updateElementById($rootScope.filenavlist, $rootScope.idactivefile, $scope.activefile.text);
            file = getElementById($rootScope.filenavlist, id);
            $rootScope.idactivefile = id;
        
            switchfile(file);
        }
    };
    
    $rootScope.setactivefile = function(id){
        updateElementById($rootScope.filenavlist, $rootScope.idactivefile, $scope.activefile.text);
        $rootScope.idactivefile = id;
        switchfile(getElementById($rootScope.filenavlist, id));
    };

    $rootScope.removefilenav = function(id){
        $rootScope.filenavlist.splice(getPositionById($rootScope.filenavlist, id), 1);
        if($rootScope.filenavlist.length !== 0){
            if($rootScope.idactivefile === id){
                $rootScope.idactivefile = $rootScope.filenavlist[0].id;
                switchfile($rootScope.filenavlist[0]);
            }
        } else {
            $rootScope.idactivefile = -1;
            switchfile({id:-1, name:"", type:0, text:""});
        }
    };
    
    $rootScope.createnewfile = function(){
        if(typeof $rootScope.namenewfile === "undefined" || typeof $rootScope.typenewfile === "undefined" || $rootScope.namenewfile.trim() === ""){
            humane.info("Errors!! Empty fields");
            return;
        }
        $rootScope.bSpin = true;
        var file = {
            iduser : $rootScope.user.id,
            idproject : $rootScope.project.id,
            nome : $rootScope.namenewfile,
            tipo : parseInt($rootScope.typenewfile)
        };
        $http({
            method : 'POST',
            url : CONFIG.url+'createfile',
            data: file,
            transformRequest : param,
            headers : {
                'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8'",
                'di' : window.localStorage.getItem("sk")
            }
        })
        .success(function(data){
            if(data.esit === 1){
                humane.info("Project created");
                var result = {
                    id : data.result.id,
                    name : $rootScope.namenewfile,
                    type : parseInt($rootScope.typenewfile),
                    text : ""
                };
                $rootScope.namenewfile = $rootScope.typenewfile = "";
        
                $rootScope.filelist.push(result);
                $rootScope.openfile(result.id);
                $rootScope.bCreatenewfile = false;
                $rootScope.bSpin = false;
            } else {
                humane.info(data.result);
                $rootScope.bSpin = false;
            };
        }).error(function(data){
            console.log(data);
            $rootScope.bSpin = false;
        });
        
    };


//  utils
    var getPositionById = function(array, id){
        for(var i in array){
            if(array[i].id === id){
                return i;
            }
        }
        return -1;
    };
    
    var isInArrayById = function(array, id){
        for(var i in array){
            if(array[i].id === id){
                return true;
            }
        }
        return false;
    };

    var getElementById = function(array, id){
        for(var i in array){
            if(array[i].id === id){
                return array[i];
            }
        }
        return null;
    };
    
    var updateElementById = function(array, id, text){
        for(var i in array){
            if(array[i].id === id){
                array[i].text = text;
            }
        }
    };
    
    var switchfile = function(elementSrc){
        $scope.activefile.id = elementSrc.id;
        $scope.activefile.name = elementSrc.name;
        $scope.activefile.type = elementSrc.type;
        $scope.activefile.text = elementSrc.text;
    }
}